# filters.py — оставляем на случай если понадобится в будущем
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
import aiosqlite

class AdminFilter(BaseFilter):
    async def __call__(self, update: Message | CallbackQuery, **kwargs) -> bool:
        db: aiosqlite.Connection = kwargs.get('db')
        if not db:
            return False
        user_id = update.from_user.id
        result = await db.execute(
            'SELECT is_admin FROM users WHERE telegram_id = ?',
            (user_id,)
        )
        user = await result.fetchone()
        return user is not None and user[0] == 1
