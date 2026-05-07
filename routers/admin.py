import aiogram
import aiosqlite
import re
from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from states.admin_state import AddBalanceState, ReduceBalanceState
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from const import ADMIN_ID
from keyboards import admin_kb

router = aiogram.Router()

def is_valid_phone(phone: str) -> bool:
    pattern = r"^\+?[0-9]{10,15}$"
    phone = phone.replace(" ", "").replace("-", "")

    return bool(re.match(pattern, phone))

def register_admin_commands(
        dispatcher: Dispatcher,
        db: aiosqlite.Connection,
    ):

    @router.message(Command("admin"))
    async def admin(message: Message):
        if message.from_user.id != ADMIN_ID:
            return
        else:
            await message.answer("Вы в админ-зоне", reply_markup=admin_kb)
            

    @router.callback_query()
    async def callbacks(call: CallbackQuery, state: FSMContext):
        
        await call.answer()

        if call.data == "add_balance":

            await call.message.answer("Введите сумму:")

            await state.set_state(AddBalanceState.amount)

        elif call.data == "reduce_balance":
            await call.message.answer("Введите сумму:")

            await state.set_state(ReduceBalanceState.amount)
            
        elif call.data == "change_number":
            ...
        elif call.data == "users":
            ...
        elif call.data == "admins":
            ...
        elif call.data == "tasks":
            ...
        elif call.data == "requests":
            ...

    @router.message(AddBalanceState.amount)
    async def get_amount(message: Message, state: FSMContext):

        await state.update_data(amount=message.text)

        await db.commit()

        await message.answer("Введите id")

        await state.set_state(AddBalanceState.id)

    @router.message(AddBalanceState.id)
    async def get_id(message: Message, state: FSMContext):

        await state.update_data(id=message.text)

        data = await state.get_data()

        result = await db.execute(
            '''
            SELECT balance
            FROM users
            WHERE user_id = (?)
            ''',
            (int(data['id']),)
        )

        current_balance = await result.fetchone()

        current_balance = current_balance[0]

        res = int(current_balance) + int(data['amount'])

        await db.execute(
            '''
            UPDATE users
            SET balance = ?
            WHERE user_id = ?
            ''',
            (res, int(data["id"]))
        )

        balance = await db.execute(
            '''
            SELECT balance
            FROM users
            WHERE user_id = (?)
            ''',
            (int(data['id']),)
        )

        balance = await balance.fetchone()

        balance = balance[0]

        await message.answer(f"Ваш баланс {int(balance)}", reply_markup=admin_kb)

        await state.clear()

    @router.message(AddBalanceState.amount)
    async def get_amount(message: Message, state: FSMContext):

        await state.update_data(amount=message.text)

        await db.commit()

        await message.answer("Введите id")

        await state.set_state(AddBalanceState.id)

    @router.message(AddBalanceState.id)
    async def get_id(message: Message, state: FSMContext):

        await state.update_data(id=message.text)

        data = await state.get_data()

        result = await db.execute(
            '''
            SELECT balance
            FROM users
            WHERE user_id = (?)
            ''',
            (int(data['id']),)
        )

        current_balance = await result.fetchone()

        current_balance = current_balance[0]
        if res >= 0:
            res = int(current_balance) - int(data['amount'])

            await db.execute(
                '''
                UPDATE users
                SET balance = ?
                WHERE user_id = ?
                ''',
                (res, int(data["id"]))
            )

            balance = await db.execute(
                '''
                SELECT balance
                FROM users
                WHERE user_id = (?)
                ''',
                (int(data['id']),)
            )

            balance = await balance.fetchone()

            balance = balance[0]

            await message.answer(f"Ваш баланс {int(balance)}", reply_markup=admin_kb)

            await state.clear()
        else:
            await message.answer(f"Недостаточно средств", reply_markup=admin_kb)


    @router.message(Command("add"))
    async def add_money(message: Message):
        
        try:
            _, user_id, amount = message.text.split()

            amount = int(amount)
            user_id = int(user_id)

            await db.execute('''
                UPDATE users
                SET balance = balance + ?
                WHERE user_id = ?;
                ''', (amount, user_id)
                )
            await db.commit()

            await message.answer("Начислено ✅")

        except Exception as e:
            print(e)
            await message.answer("Ошибка начисления.")

    @router.message(Command("reduce"))
    async def reduce_money(message: Message):
        
        try:
            _, user_id, amount = message.text.split()

            user_id = int(user_id)
            amount = int(amount)

            result = await db.execute(
                '''
                SELECT balance
                FROM users
                WHERE user_id = ?
                ''',
                (user_id,)
            )

            result = await result.fetchone()

            if result is None:
                await message.answer("Пользователь не найден.")
                return

            current_balance = result[0]

            if current_balance < amount:
                await message.answer("Не хватает средств.")
                return

            await db.execute(
                '''
                UPDATE users
                SET balance = balance - ?
                WHERE user_id = ?;
                ''',
                (amount, user_id)
            )

            await db.commit()

            await message.answer("Списано ✅")
            
        except Exception as e:
            print(e)
            await message.answer("Ошибка списания.")

    @router.message(Command("phone"))
    async def set_phone(message: Message):
        
        try:
            
            _, user_id, phone = message.text.split()

            user_id = int(user_id)

            if not is_valid_phone(phone):
                await Exception

            await db.execute(
                '''
                UPDATE users
                SET phone = (?)
                WHERE user_id = (?);
                ''',
                (phone, user_id)
            )

            await db.commit()

            await message.answer("Номер обновлен ✅")
        except Exception as e:
            print(e)
            await message.answer("Ошибка установления номера.")