import aiosqlite
from dotenv import load_dotenv
from aiogram.types import Message


async def is_admin(
        user_id: int,
        db: aiosqlite.Connection
    ) -> bool:
    result = await db.execute(
        'SELECT is_admin FROM users WHERE telegram_id = ?',
        (user_id,)
    )
    user = await result.fetchone()
    return user is not None and user[0] == 1
