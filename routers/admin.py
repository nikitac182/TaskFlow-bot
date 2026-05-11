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

async def render_admin_page(
    target: Message | CallbackQuery,
    page=0,
):

    offset = page * 20

    result_2 = await db.execute(
            '''
            SELECT id, telegram_id, username, created_at, is_admin
            FROM users
            LIMIT 20 OFFSET ?
            ''',
            (offset + 20, )
        )

    items_2 = await result_2.fetchall()

    if page == 0:
        variable_admin_kb = [
            [InlineKeyboardButton(text='Открыть пользователя.', callback_data='open_user')],
            [
                InlineKeyboardButton(text='➡️', callback_data=f'next_page_{page + 1}')
            ],
            [InlineKeyboardButton(text='🔙 Назад', callback_data='back_admin')]
        ]
    elif len(items_2) == 0:
        variable_admin_kb = [
            [InlineKeyboardButton(text='Открыть пользователя.', callback_data='open_user')],
            [
                InlineKeyboardButton(text='⬅️', callback_data=f'back_page_{page - 1}'),
            ],
            [InlineKeyboardButton(text='🔙 Назад', callback_data='back_admin')]
        ]
    else:
        variable_admin_kb = [
            [InlineKeyboardButton(text='Открыть пользователя.', callback_data='open_user')],
            [
                InlineKeyboardButton(text='⬅️', callback_data=f'back_page_{page - 1}'),
                InlineKeyboardButton(text='➡️', callback_data=f'next_page_{page + 1}')
            ],
            [InlineKeyboardButton(text='🔙 Назад', callback_data='back_admin')]
        ]

    result = await db.execute(
            '''
            SELECT id, telegram_id, username, created_at, is_admin
            FROM users
            LIMIT 20 OFFSET ?
            ''',
            (offset, )
        )
    caption = f'👥 Пользователи\n'
    items = await result.fetchall()
    for item in items:
        id, telegram_id, username, created_at, is_admin = item
        caption += f'id: {id} -> @{username}\n'
    admin_kb_2 = InlineKeyboardMarkup(
        inline_keyboard=variable_admin_kb
    )
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(caption, reply_markup=admin_kb_2)
    else:
        await target.answer(caption, reply_markup=admin_kb_2)



@router.message(CommandStart())
async def render(message: Message):
    await message.answer("Вы в админ-зоне", reply_markup=admin_kb)
