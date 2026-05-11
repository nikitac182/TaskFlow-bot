import aiogram
import aiosqlite

from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from const import *
from keyboards import *
from states.user_state import WithDrawState


router = aiogram.Router()
bot: aiogram.Bot | None = None
db: aiosqlite.Connection | None = None
admins = None


async def render_tasks_page(
    target: Message | CallbackQuery,
    page: int = 0,
) -> None:

    user_id = target.from_user.id
    offset = page * 5

    tasks_cursor = await db.execute(
        '''
        SELECT title, description, status, id
        FROM tasks
        WHERE assigned_to = ?
        LIMIT 5 OFFSET ?
        ''',
        (user_id, offset),
    )
    tasks: list[tuple] = await tasks_cursor.fetchall()

    next_tasks_cursor = await db.execute(
        '''
        SELECT id FROM tasks
        WHERE assigned_to = ?
        LIMIT 1 OFFSET ?
        ''',
        (user_id, offset + 5),
    )
    has_next = bool(await next_tasks_cursor.fetchone())

    if not tasks:
        text = (
            '📭 У вас пока нет задач.\n\n'
            'Когда администратор назначит вам задачу,\n'
            'она появится здесь.'
        )
        if isinstance(target, CallbackQuery):
            await target.message.edit_text(text)
        else:
            await target.answer(text)
        return

    tasks_text = ''
    buttons: list[list[InlineKeyboardButton]] = []

    for task in tasks:
        title, _, status, task_id = task
        tasks_text += (
            f'{status_form[status][0]} Задача: {title}\n'
            f'Статус: {status_form[status][1]}\n'
            f'_________________\n'
        )
        buttons.append([
            InlineKeyboardButton(
                text=f"Описание для '{title}'",
                callback_data=f'task_data_{task_id}',
            )
        ])

    nav_row: list[InlineKeyboardButton] = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text='⬅️', callback_data=f'back_{page - 1}'))
    if has_next:
        nav_row.append(InlineKeyboardButton(text='➡️', callback_data=f'page_{page + 1}'))
    if nav_row:
        buttons.append(nav_row)

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(tasks_text, reply_markup=keyboard)
    else:
        await target.answer(tasks_text, reply_markup=keyboard)


async def render_task_description(
    callback: CallbackQuery,
    task_id: int,
) -> None:

    cursor = await db.execute(
        'SELECT * FROM tasks WHERE id = ?',
        (task_id,),
    )
    (
        task_id, title, description, status,
        assigned_to, created_by, created_at,
        materials, deadline,
    ) = await cursor.fetchone()

    user = await bot.get_chat(assigned_to)

    text = (
        f'📋 Задача #{task_id}\n\n'
        f'━━━━━━━━━━━━━━━\n\n'
        f'📝 Название:\n{title}\n\n'
        f'📄 Описание:\n{description}\n\n'
        f'📎 Материалы:\n{materials}\n\n'
        f'⏰ Дедлайн:\n{deadline}\n\n'
        f'📌 Статус:\n{status_form[status][0]} {status_form[status][1]}\n\n'
        f'━━━━━━━━━━━━━━━\n\n'
        f'👤 Исполнитель:\n@{user.username}'
    )

    await callback.message.edit_text(text, reply_markup=back_kb)


async def render_submission_menu(callback: CallbackQuery) -> None:

    text = (
        '📎 Отправьте выполнение задачи\n\n'
        'Можно отправить:\n\n'
        '• текст\n'
        '• ссылку\n'
        '• фото\n'
        '• файл\n'
        '• архив\n'
        '• видео\n\n'
        '━━━━━━━━━━━━━━━\n\n'
        'После отправки администратор\n'
        'получит вашу работу на проверку.'
    )

    await callback.message.edit_text(text, reply_markup=back_kb_2)


# ─────────────────────────── handlers ───────────────────────────

@router.message(CommandStart())
async def start(message: Message) -> None:

    await db.execute(
        'INSERT OR IGNORE INTO users (telegram_id, username) VALUES (?, ?)',
        (message.from_user.id, message.from_user.username),
    )
    await db.commit()
    await message.answer('Выбери кнопку:', reply_markup=kb)


@router.message(lambda m: m.text == 'Профиль')
async def profile(message: Message) -> None:

    done_cursor = await db.execute(
        'SELECT COUNT(*) FROM tasks WHERE assigned_to = ? AND status = "accepted"',
        (message.from_user.id,),
    )
    active_cursor = await db.execute(
        'SELECT COUNT(*) FROM tasks WHERE assigned_to = ? AND status = "in_progress"',
        (message.from_user.id,),
    )

    tasks_done = (await done_cursor.fetchone())[0]
    tasks_active = (await active_cursor.fetchone())[0]

    text = (
        f'👋 Добро пожаловать,\n'
        f'<b>{message.from_user.full_name}</b>\n\n'
        f'🪪 <b>Ваш профиль:</b>\n\n'
        f'• ID: <code>{message.from_user.id}</code>\n'
        f'• Username: @{message.from_user.username}\n\n'
        f'📊 <b>Статистика</b>\n\n'
        f'├ Выполнено задач: {tasks_done}\n'
        f'├ Активных задач: {tasks_active}\n'
        f'└ Рейтинг: —\n\n'
        f'🚀 Продолжай выполнять задания!'
    )

    await message.answer(text, parse_mode='HTML')


@router.message(lambda m: m.text == 'Мои задачи')
async def open_tasks(message: Message) -> None:
    await render_tasks_page(message, page=0)


@router.message(lambda m: m.text == 'Поддержка')
async def support(message: Message) -> None:
    await message.answer(f'По всем вопросам:\n{ADMIN_USERNAME}')

@router.message(WithDrawState.request)
async def handle_submission(message: Message, state: FSMContext) -> None:

    content = message.content_type

    match content:
        case 'text':
            file_id, text = None, message.text
        case 'photo':
            file_id, text = message.photo[-1].file_id, message.caption or 'PHOTO'
        case 'document':
            file_id, text = message.document.file_id, message.caption or 'DOCUMENT'
        case 'video':
            file_id, text = message.video.file_id, message.caption or 'VIDEO'
        case 'audio':
            file_id, text = message.audio.file_id, 'AUDIO'
        case 'voice':
            file_id, text = message.voice.file_id, 'VOICE'
        case _:
            await message.answer('❌ Неподдерживаемый тип файла')
            return

    task_id = (await state.get_data()).get('task_id')

    await db.execute(
        'INSERT INTO submissions (task_id, user_id, file_id, text, type) VALUES (?, ?, ?, ?, ?)',
        (task_id, message.from_user.id, file_id, text, content),
    )
    await db.commit()

    await message.answer('✅ Выполнение успешно отправлено')
    await state.clear()