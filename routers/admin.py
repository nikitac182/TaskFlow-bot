# admin.py
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
router.message.filter(lambda m: m.from_user.id == ADMIN_ID)

bot: aiogram.Bot | None = None
db: aiosqlite.Connection | None = None


@router.message(CommandStart())
async def render(message: Message):
    
    await message.answer("Вы в админ-зоне", reply_markup=admin_kb)
    
# ✅ Лучше использовать фильтр прямо в декораторе
@router.callback_query(lambda c: c.data == 'k')
async def callbacks(call: CallbackQuery):
    await call.message.edit_text("123")
    await call.answer()

@router.message(lambda m: m.text == 'Пользователи')
async def users_admin(message: Message):
    result = await db.execute(
            '''
            SELECT id, telegram_id, username, created_at, is_admin
            FROM users
            '''
        )
    caption = f'👥 Пользователи\n'
    items = await result.fetchall()
    for item in items:
        id, telegram_id, username, created_at, is_admin = item
        caption += f'id: {id} -> @{username}\n'
    admin_kb_2 = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Открыть пользователя.', callback_data='k')]
        ]
    )
    await message.answer(caption, reply_markup=admin_kb_2)


    
