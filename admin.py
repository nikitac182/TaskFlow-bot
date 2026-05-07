import aiosqlite
import re
from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from const import ADMIN_ID

def is_valid_phone(phone: str) -> bool:
    pattern = r"^\+?[0-9]{10,15}$"
    phone = phone.replace(" ", "").replace("-", "")

    return bool(re.match(pattern, phone))

def register_admin_commands(
        dispatcher: Dispatcher,
        db: aiosqlite.Connection,
    ):

    @dispatcher.message(Command("add"))
    async def add_money(message: Message):
        if message.from_user.id != ADMIN_ID:
            return
        
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

    @dispatcher.message(Command("reduce"))
    async def reduce_money(message: Message):

        if message.from_user.id != ADMIN_ID:
            return
        
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

    @dispatcher.message(Command("phone"))
    async def set_phone(message: Message):
        if message.from_user.id != ADMIN_ID:
            return
        
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