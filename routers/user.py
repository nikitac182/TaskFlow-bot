import aiogram
import aiosqlite
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from const import *
from keyboards import *
from states.user_state import WithDrawState
from aiogram.fsm.context import FSMContext

router = aiogram.Router()



def setup_router(
        bot,
        db: aiosqlite.Connection,
    ):

    async def my_func(
        target: CallbackQuery,
        page=0,
        is_back=False,
    ):

        start = page * 5
        end = start + 5

        offset = page * 5

        result = await db.execute(
            '''
            SELECT title, description, status, id
            FROM tasks
            WHERE assigned_to = (?)
            LIMIT 5 OFFSET ?
            ''',
            (target.from_user.id, offset)
        )

        results_tasks = await result.fetchall()

        string = ''
        buttons = []

        
        for result in results_tasks:
            
            string += f'{status_form[result[2]][0]} Задача: {result[0]}\n Статус: {status_form[result[2]][1]}\n_________________\n'

            buttons.append(
            [
                InlineKeyboardButton(
                    text=f"Описание для '{result[0]}' ",
                    callback_data=f"task_data_{result[3]}"
                    )
                ]
            )
        if page == 0:
            buttons.append(
            [InlineKeyboardButton(
                    text="➡️",
                    callback_data=f"page_{page + 1}"
                    )
                ]
            )
        else:
            buttons.append(
            [InlineKeyboardButton(text="⬅️",callback_data=f"back_{page - 1}"),
             InlineKeyboardButton(text="➡️",callback_data=f"page_{page + 1}")
             ]
            )



        on_tasks_kb = InlineKeyboardMarkup(
            inline_keyboard=buttons
        )
        if isinstance(target, CallbackQuery):
            if is_back:
                await target.message.answer(string, reply_markup=on_tasks_kb)
            else:
                await target.message.edit_text(string, reply_markup=on_tasks_kb)

        elif isinstance(target, Message):
            await target.answer(string, reply_markup=on_tasks_kb)


    @router.message(CommandStart())
    async def start(message: Message):
        await db.execute('''
            INSERT OR IGNORE INTO users (telegram_id, username) VALUES (?, ?);
            ''', (message.from_user.id, message.from_user.username)
        )
        await db.commit()

        await message.answer('Выбери кнопку: ', reply_markup=kb)

    @router.message(lambda message: message.text == 'Профиль')
    async def profile(message: Message):
        result = await db.execute(
            '''
            SELECT COUNT(*)  
            FROM tasks 
            WHERE assigned_to = ? AND status = "accepted"
            ''', (message.from_user.id,)
        )
        result = await result.fetchone()

        result_2 = await db.execute(
            '''
            SELECT COUNT(*)  
            FROM tasks 
            WHERE assigned_to = ? AND status = "in_progress"
            ''', (message.from_user.id,)
        )
        result_2 = await result_2.fetchone()

        tasks_done = result[0]
        active_tasks = result_2[0]
        rating = None

        await message.answer(
    f"""
👋 Добро пожаловать, <b>{message.from_user.full_name}</b>

🪪 <b>Ваш профиль:</b>

• ID: <code>{message.from_user.id}</code>
• Username: @{message.from_user.username}

📊 <b>Статистика</b>
├ Выполнено задач: {tasks_done}
├ Активных задач: {active_tasks}
└ Рейтинг: {rating}

🚀 Продолжай выполнять задания!
""",
    parse_mode="HTML"
)
    @router.message(lambda message: message.text == 'Мои задачи')
    async def task_menu(message: Message):

        await my_func(message, page=0)

    @router.callback_query()
    async def callbacks(call: CallbackQuery):

        await call.answer()

        current_page = 0

        if call.data.startswith('task_data_'):

            id = call.data.split('_')[-1]

            result = await db.execute(
                '''
                SELECT *
                FROM tasks
                WHERE id = (?)
                ''',
                (id, )
            )

            result = await result.fetchone()

            id, title, description, status, assigned_to, created_by, created_at, materials, deadline = result

            user = await bot.get_chat(1143200581)

            string_task = f'''
📋 Задача {id}

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
            await call.message.edit_text(string_task, reply_markup=back_kb)

        elif call.data == 'back':

            await my_func(call, page=current_page)
        
        elif call.data.startswith('page'):
            page = int(call.data.split('_')[-1])
            current_page += 1
            await my_func(call, page=page)



    @router.message(lambda message: message.text == 'Поддержка')
    async def support(message: Message):
        await message.answer(
            f'По всем вопросам:\n{ ADMIN_USERNAME }'
        )
