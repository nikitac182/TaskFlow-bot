import asyncio
import aiosqlite
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from const import ADMIN_ID, ADMIN_USERNAME, TOKEN
from keyboards import kb, tasks_kb, on_tasks_kb
from admin import register_admin_commands

tasks = {
    "1": "Задание №1:\nПодпишись на канал и отправь скрин",
    "2": "Задание №2:\nПоставь лайк под постом",
    "3": "Задание №3:\nПригласи друга",
    "4": "Задание №4:\nЗайди на сайт бота",
    "5": "Задание №5:\n..."
}


bot = Bot(token=TOKEN)
dp = Dispatcher()
db = None


@dp.message(CommandStart())
async def start(message: Message):
    await db.execute('''
        INSERT OR IGNORE INTO users (user_id) VALUES (?);
        ''', (message.from_user.id,)
    )
    await db.commit()

    await message.answer('Выбери кнопку: ', reply_markup=kb)


class WithDrawState(StatesGroup):
    amount = State()
    number = State()


@dp.message(lambda message: message.text == 'Профиль')
async def profile(message: Message):
    result = await db.execute('''
        SELECT balance FROM users WHERE user_id = ?
        ''', (message.from_user.id,)
    )

    result = await result.fetchone()

    balance = result[0]
    await message.answer(f'Твой баланс {balance} руб.')

@dp.message(lambda message: message.text == 'Задания')
async def task_menu(message: Message):
    await message.answer('Выбери номер задания', reply_markup=tasks_kb)
    
@dp.message(lambda message: message.text in tasks)
async def send_task(message: Message):
    await message.answer(tasks[message.text], reply_markup=on_tasks_kb)

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
    
    result = await db.execute(
        '''SELECT balance FROM users WHERE user_id = ?''',
        (message.from_user.id,)
    )

    result = await result.fetchone()

    balance = result[0]

    if amount > balance:
        await message.answer('Недостаточно средств')
        return 
    
    await state.update_data(amount=amount)

    await message.answer('Введите номер телефона')
    await state.set_state(WithDrawState.number)

@dp.message(WithDrawState.number)
async def frocess_withdraw_number(message: Message, state: FSMContext):

    data = await state.get_data()
    amount = data['amount']
    card = message.text

    await db.execute(
        '''
        UPDATE users
        SET phone = ?
        WHERE user_id = ?;
        ''',
        (card, message.from_user.id)
    )

    await db.commit()

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
    global db

    db = await aiosqlite.connect("sqlite.db")

    register_admin_commands(dp, db)

    await db.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 0,
        phone TEXT
    )
    """
    )

    await db.commit()
    
    try:
        await dp.start_polling(bot)
    finally:
        await db.close()

if __name__ == '__main__':
    asyncio.run(main())
