import aiogram
import aiosqlite

from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from const import *
from keyboards import *
from states.user_state import WithDrawState


router = aiogram.Router()


def setup_router(
    bot: aiogram.Bot,
    db: aiosqlite.Connection,
) -> None:

    async def render_tasks_page(
        target: Message | CallbackQuery,
        page: int = 0,
        is_back: bool = False,
    ) -> None:

        offset: int = page * 5

        tasks_cursor = await db.execute(
            '''
            SELECT title, description, status, id
            FROM tasks
            WHERE assigned_to = ?
            LIMIT 5 OFFSET ?
            ''',
            (target.from_user.id, offset)
        )

        tasks: list[tuple] = await tasks_cursor.fetchall()

        next_page_offset: int = (page + 1) * 5

        next_tasks_cursor = await db.execute(
            '''
            SELECT title, description, status, id
            FROM tasks
            WHERE assigned_to = ?
            LIMIT 5 OFFSET ?
            ''',
            (target.from_user.id, next_page_offset)
        )

        next_tasks: list[tuple] = await next_tasks_cursor.fetchall()

        keyboard_buttons: list[list[InlineKeyboardButton]] = []

        if not tasks:

            empty_text: str = '''
📭 У вас пока нет задач.

Когда администратор назначит вам задачу,
она появится здесь.
'''

            if isinstance(target, CallbackQuery):
                await target.message.edit_text(empty_text)

            elif isinstance(target, Message):
                await target.answer(empty_text)

            return

        tasks_text: str = ''

        for task in tasks:

            task_title: str = task[0]
            task_status: str = task[2]
            task_id: int = task[3]

            tasks_text += (
                f'{status_form[task_status][0]} '
                f'Задача: {task_title}\n'
                f'Статус: {status_form[task_status][1]}\n'
                f'_________________\n'
            )

            keyboard_buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"Описание для '{task_title}'",
                        callback_data=f"task_data_{task_id}"
                    )
                ]
            )

        if page == 0:

            keyboard_buttons.append(
                [
                    InlineKeyboardButton(
                        text="➡️",
                        callback_data=f"page_{page + 1}"
                    )
                ]
            )

        elif not next_tasks:

            keyboard_buttons.append(
                [
                    InlineKeyboardButton(
                        text="⬅️",
                        callback_data=f"back_{page - 1}"
                    )
                ]
            )

        elif page > 0:

            keyboard_buttons.append(
                [
                    InlineKeyboardButton(
                        text="⬅️",
                        callback_data=f"back_{page - 1}"
                    ),

                    InlineKeyboardButton(
                        text="➡️",
                        callback_data=f"page_{page + 1}"
                    )
                ]
            )

        tasks_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
            inline_keyboard=keyboard_buttons
        )

        if isinstance(target, CallbackQuery):

            if is_back:
                await target.message.answer(
                    tasks_text,
                    reply_markup=tasks_keyboard
                )

            else:
                await target.message.edit_text(
                    tasks_text,
                    reply_markup=tasks_keyboard
                )

        elif isinstance(target, Message):

            await target.answer(
                tasks_text,
                reply_markup=tasks_keyboard
            )

    async def render_task_description(
        callback: CallbackQuery,
        task_id: int,
    ) -> None:

        task_cursor = await db.execute(
            '''
            SELECT *
            FROM tasks
            WHERE id = ?
            ''',
            (task_id,)
        )

        task_data: tuple = await task_cursor.fetchone()

        (
            task_id,
            title,
            description,
            status,
            assigned_to,
            created_by,
            created_at,
            materials,
            deadline
        ) = task_data

        user = await bot.get_chat(assigned_to)

        task_text: str = f'''
📋 Задача #{task_id}

━━━━━━━━━━━━━━━

📝 Название:
{title}

📄 Описание:
{description}

📎 Материалы:
{materials}

⏰ Дедлайн:
{deadline}

📌 Статус:
{status_form[status][0]} {status_form[status][1]}

━━━━━━━━━━━━━━━

👤 Исполнитель:
@{user.username}
'''

        await callback.message.edit_text(
            task_text,
            reply_markup=back_kb
        )

    async def render_submission_menu(
        callback: CallbackQuery,
    ) -> None:

        submission_text: str = '''
📎 Отправьте выполнение задачи

Можно отправить:

• текст
• ссылку
• фото
• файл
• архив
• видео

━━━━━━━━━━━━━━━

После отправки администратор
получит вашу работу на проверку.
'''

        await callback.message.edit_text(
            submission_text,
            reply_markup=back_kb_2
        )

    @router.message(CommandStart())
    async def start(message: Message) -> None:

        await db.execute(
            '''
            INSERT OR IGNORE INTO users
            (telegram_id, username)
            VALUES (?, ?)
            ''',
            (
                message.from_user.id,
                message.from_user.username
            )
        )

        await db.commit()

        await message.answer(
            'Выбери кнопку:',
            reply_markup=kb
        )

    @router.message(lambda message: message.text == 'Профиль')
    async def profile(message: Message) -> None:

        completed_tasks_cursor = await db.execute(
            '''
            SELECT COUNT(*)
            FROM tasks
            WHERE assigned_to = ?
            AND status = "accepted"
            ''',
            (message.from_user.id,)
        )

        completed_tasks = await completed_tasks_cursor.fetchone()

        active_tasks_cursor = await db.execute(
            '''
            SELECT COUNT(*)
            FROM tasks
            WHERE assigned_to = ?
            AND status = "in_progress"
            ''',
            (message.from_user.id,)
        )

        active_tasks = await active_tasks_cursor.fetchone()

        tasks_done_count: int = completed_tasks[0]
        active_tasks_count: int = active_tasks[0]

        rating: str | None = None

        profile_text: str = f"""
👋 Добро пожаловать,
<b>{message.from_user.full_name}</b>

🪪 <b>Ваш профиль:</b>

• ID: <code>{message.from_user.id}</code>
• Username: @{message.from_user.username}

📊 <b>Статистика</b>

├ Выполнено задач: {tasks_done_count}
├ Активных задач: {active_tasks_count}
└ Рейтинг: {rating}

🚀 Продолжай выполнять задания!
"""

        await message.answer(
            profile_text,
            parse_mode="HTML"
        )

    @router.message(lambda message: message.text == 'Мои задачи')
    async def open_tasks(message: Message) -> None:

        await render_tasks_page(
            message,
            page=0
        )

    @router.callback_query()
    async def callbacks(
        callback: CallbackQuery,
        state: FSMContext
    ) -> None:

        await callback.answer()

        state_data: dict = await state.get_data()

        current_page: int = state_data.get(
            'current_page',
            0
        )

        current_task_id: int = state_data.get(
            'task_id',
            0
        )

        if callback.data.startswith('task_data_'):

            task_id: int = int(
                callback.data.split('_')[-1]
            )

            await state.update_data(
                task_id=task_id
            )

            await render_task_description(
                callback,
                task_id
            )

        elif callback.data == 'p_back':

            await render_tasks_page(
                callback,
                page=current_page
            )

        elif callback.data == 'p_back_2':

            await render_task_description(
                callback,
                task_id=current_task_id
            )

        elif (
            callback.data.startswith('page_')
            or callback.data.startswith('back_')
        ):

            page: int = int(
                callback.data.split('_')[-1]
            )

            await state.update_data(
                current_page=page
            )

            await render_tasks_page(
                callback,
                page=page
            )

        elif callback.data == 'make_task':

            await render_submission_menu(
                callback
            )

            await state.set_state(
                WithDrawState.request
            )

    @router.message(
        lambda message: message.text == 'Поддержка'
    )
    async def support(message: Message) -> None:

        await message.answer(
            f'По всем вопросам:\n{ADMIN_USERNAME}'
        )

    @router.message(WithDrawState.request)
    async def handle_submission(
        message: Message,
        state: FSMContext
    ) -> None:
        
        user_request = message.content_type

        if user_request == "text":
            file_id = None
            text = message.text

        elif user_request == "photo":
            file_id = message.photo[-1].file_id
            text = message.caption or "PHOTO"

        elif user_request == "document":
            file_id = message.document.file_id
            text = message.caption or "DOCUMENT"

        elif user_request == "video":
            file_id = message.video.file_id
            text = message.caption or "VIDEO"

        elif user_request == "audio":
            file_id = message.audio.file_id
            text = "AUDIO"

        elif user_request == "voice":
            file_id = message.voice.file_id
            text = "VOICE"

        else:
            await message.answer("❌ Неподдерживаемый тип файла")
            return

        state_data: dict = await state.get_data()

        task_id = state_data.get("task_id")

        await db.execute(
            '''
            INSERT INTO submissions
            (task_id, user_id, file_id, text, type)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (
                task_id,
                message.from_user.id,
                file_id,
                text,
                user_request
            )
        )

        await db.commit()

        await message.answer(
            "✅ Выполнение успешно отправлено"
        )

        await state.clear()
        