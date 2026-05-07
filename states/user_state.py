from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from bot import db, dp

class WithDrawState(StatesGroup):
    amount = State()
    number = State()

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