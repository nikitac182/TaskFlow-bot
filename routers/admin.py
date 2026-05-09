import aiogram
import aiosqlite

from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from const import *
from keyboards import *
from states.admin_state import *


router = aiogram.Router()

def setup_admin_router(
        bot: aiogram.Bot,
        db: aiosqlite.Connection,
):

    @router.message()
    async def render(message: Message):

        result = await db.execute(
            '''
            SELECT task_id, user_id, text, file_id, type
            FROM submissions
            '''
        )

        items = await result.fetchall()

        for item in items:
            task_id, user_id, text, file_id, type_item = item
            user = await bot.get_chat(user_id)
            username = user.username
            if not file_id:
                caption = (
                    f"📋 Задача #{task_id}\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"👤 Исполнитель: @{username}\n"
                    f"🆔 User ID: {user_id}\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"📝 Ответ:\n{text}\n"
                    f"━━━━━━━━━━━━━━━\n"
                )
                await message.answer(caption)
                continue
            file = await bot.get_file(file_id)
            file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
            caption = (
                f"📋 Задача #{task_id}\n"
                f"━━━━━━━━━━━━━━━\n"
                f"👤 Исполнитель: @{username}\n"
                f"🆔 User ID: {user_id}\n"
                f"━━━━━━━━━━━━━━━\n"
                f"📝 Ответ:\n{text}\n"
                f"━━━━━━━━━━━━━━━\n"
                )
            kbs = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📎 Скачать файл", url=file_url)]
                ])
            await message.answer(caption, reply_markup=kbs)