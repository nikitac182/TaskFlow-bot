import asyncio
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from const import *

tasks = {
    "1": "Задание №1:\nПодпишись на канал и отправь скрин",
    "2": "Задание №2:\nПоставь лайк под постом",
    "3": "Задание №3:\nПригласи друга",
    "4": "Задание №4:\nЗайди на сайт бота",
    "5": "Задание №5:\n..."
}

con = sqlite3.connect('sqlite.db')
cur = con.cursor()

cur.execute(''' 
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    number INTEGER
    );
''')

con.commit()

bot = Bot(token=TOKEN)
dp = Dispatcher()

kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Профиль")],
        [KeyboardButton(text="Задания")],
        [KeyboardButton(text="Поддержка")],
        [KeyboardButton(text="Вывод")],
    ],
    resize_keyboard=True,
)

tasks_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="1"), KeyboardButton(text="2")],
        [KeyboardButton(text="3")],
        [KeyboardButton(text="4")],
        [KeyboardButton(text="Назад")]
    ], 
    resize_keyboard=True,
)

@dp.message(CommandStart())
async def start(message: Message):
    cur.execute('''
        INSERT OR IGNORE INTO users (user_id) VALUES (?);
        ''', (message.from_user.id,)
    )
    con.commit()

    await message.answer('Выбери кнопку: ', reply_markup=kb)

class WithDrawState(StatesGroup):
    amount = State()
    number = State()


@dp.message(Command("add"))
async def add_money(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        _, user_id, amount = message.text.split()

        cur.execute('''
            UPDATE users SET balance = balance + ? WHERE user_id = ?;
            ''', (int(amount), int(user_id))
            )
        con.commit()

        await message.answer("Начислено ✅")

    except:
        await message.answer("Ошибка начисления")

@dp.message(Command("reduce"))
async def reduce_money(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        _, user_id, amount = message.text.split()

        result = cur.execute(
            '''SELECT balance FROM users WHERE user_id = ?''',
            (int(user_id),)
        ).fetchone()

        if result is None:
            await message.answer("Пользователь не найден.")

        current_balance = result[0]

        if (int(current_balance) - int(amount)) < 0:
            await message.answer("Не хватает средств")
            return

        cur.execute('''
            UPDATE users SET balance = balance - ? WHERE user_id = ?;
            ''', (int(amount), int(user_id))
        )
        con.commit()
        await message.answer("Списано ✅")
        
    except:
        await message.answer("Произошла ошибка списания")

@dp.message(lambda message: message.text == 'Профиль')
async def profile(message: Message):
    cur.execute('''
        SELECT balance FROM users WHERE user_id = ?
        ''', (message.from_user.id,)
    )
    balance = cur.fetchone()[0]
    await message.answer(f'Твой баланс {balance} руб.')

@dp.message(lambda message: message.text == 'Задания')
async def task_menu(message: Message):
    await message.answer('Выбери номер задания', reply_markup=tasks_kb)
    
@dp.message(lambda message: message.text in tasks)
async def send_task(message: Message):
    await message.answer(tasks[message.text])

@dp.message(lambda message: message.text == 'Назад')
async def back(message: Message):
    await message.answer("Главное меню", reply_markup=kb)

@dp.message(lambda message: message.text == 'Поддержка')
async def support(message: Message):
    await message.answer(
        f'По всем вопросам:\n{ ADMIN_USERNAME }'
    )

@dp.message(lambda message: message.text == "Вывод")
async def withdraw(message: Message, state: FSMContext):
    await message.answer('Введите сумму для вывода:')
    await state.set_state(WithDrawState.amount)

@dp.message(WithDrawState.amount)
async def process_withdraw(message: Message, state: FSMContext):

    if not message.text.isdigit():
        await message.answer('Введите число')
        return 
    
    amount = int(message.text)
    
    balance = cur.execute(
        '''SELECT balance FROM users WHERE user_id = ?''',
        (message.from_user.id,)
    ).fetchone()[0]

    if amount > balance:
        await message.answer('Недостаточно средств')
        return 
    
    await state.update_data(amount=amount)

    await message.answer('Введите номер телеефона')
    await state.set_state(WithDrawState.number)

@dp.message(WithDrawState.number)
async def frocess_withdraw_number(message: Message, state: FSMContext):

    data = await state.get_data()
    amount = data['amount']
    card = message.text


    await bot.send_message(
        ADMIN_ID,
        f"Заявка на вывод:\n"
        f"Username: @{message.from_user.username}\n"
        f"Сумма: {amount} руб.\n"
        f"Номер телефона: {card}."
    )

    await message.answer('Ваша заявка отправлена ✅')

    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
