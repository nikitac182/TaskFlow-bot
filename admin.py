from sqlite3 import Connection, Cursor
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from const import ADMIN_ID

def register_admin_commands(
        dispatcher: Dispatcher,
        bot: Bot,
        connection: Connection,
        cursor: Cursor
    ):

    @dispatcher.message(Command("add"))
    async def add_money(message: Message):
        if message.from_user.id != ADMIN_ID:
            return
        
        try:
            _, user_id, amount = message.text.split()

            cursor.execute('''
                UPDATE users SET balance = balance + ? WHERE user_id = ?;
                ''', (int(amount), int(user_id))
                )
            connection.commit()

            await message.answer("Начислено ✅")

        except:
            await message.answer("Ошибка начисления")

    @dispatcher.message(Command("reduce"))
    async def reduce_money(message: Message):
        if message.from_user.id != ADMIN_ID:
            return
        
        try:
            _, user_id, amount = message.text.split()

            result = cursor.execute(
                '''SELECT balance FROM users WHERE user_id = ?''',
                (int(user_id),)
            ).fetchone()

            if result is None:
                await message.answer("Пользователь не найден.")

            current_balance = result[0]

            if (int(current_balance) - int(amount)) < 0:
                await message.answer("Не хватает средств")
                return

            cursor.execute('''
                UPDATE users SET balance = balance - ? WHERE user_id = ?;
                ''', (int(amount), int(user_id))
            )
            connection.commit()
            await message.answer("Списано ✅")
            
        except:
            await message.answer("Произошла ошибка списания")