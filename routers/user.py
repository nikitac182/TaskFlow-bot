import aiogram
from aiogram.types import Message
from aiogram.filters import CommandStart
from const import *
from keyboards import *
from states.user_state import WithDrawState
from aiogram.fsm.context import FSMContext

router = aiogram.Router()

def setup_router(bot, db, tasks):

    
    @router.message(CommandStart())
    async def start(message: Message):
        await db.execute('''
            INSERT OR IGNORE INTO users (user_id) VALUES (?);
            ''', (message.from_user.id,)
        )
        await db.commit()

        await message.answer('Выбери кнопку: ', reply_markup=kb)

    @router.message(lambda message: message.text == 'Профиль')
    async def profile(message: Message):
        result = await db.execute('''
            SELECT balance FROM users WHERE user_id = ?
            ''', (message.from_user.id,)
        )

        result = await result.fetchone()

        balance = result[0]
        await message.answer(f'Твой баланс {balance} руб.')

    @router.message(lambda message: message.text == 'Задания')
    async def task_menu(message: Message):
        await message.answer('Выбери номер задания', reply_markup=tasks_kb)
        
    @router.message(lambda message: message.text in tasks)
    async def send_task(message: Message):
        await message.answer(tasks[message.text], reply_markup=on_tasks_kb)

    @router.message(lambda message: message.text == 'Назад')
    async def back(message: Message):
        await message.answer("Главное меню", reply_markup=kb)

    @router.message(lambda message: message.text == 'Поддержка')
    async def support(message: Message):
        await message.answer(
            f'По всем вопросам:\n{ ADMIN_USERNAME }'
        )

    @router.message(lambda message: message.text == "Вывод")
    async def withdraw(message: Message, state: FSMContext):
        await message.answer('Введите сумму для вывода:')
        await state.set_state(WithDrawState.amount)

    @router.message(WithDrawState.amount)
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

    @router.message(WithDrawState.number)
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