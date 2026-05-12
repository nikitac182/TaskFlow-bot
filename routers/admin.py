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
admins = None

db: aiosqlite.Connection | None = None
bot: aiogram.Bot | None = None


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
async def render_admin_zone_menu(
    target: Message | CallbackQuery,
):
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(f'Вы в админ-зоне', reply_markup=admin_kb)
    else:
        await target.answer(f'Вы в админ-зоне', reply_markup=admin_kb)

async def render_user_full_info(
        
    target: Message | CallbackQuery,
    id=None
):
    result = await db.execute(
        '''
        SELECT id, telegram_id, username, created_at, is_admin
        FROM users
        WHERE id = ?
        ''',
        (id, )
    )

    user = await result.fetchone()

    id, telegram_id, username, created_at, is_admin = user

    caption = f'''
👤 Пользователь #{id}

━━━━━━━━━━━━━━━

🆔 Telegram ID:
{telegram_id}

👤 Username:
@{username}

🛡 Роль:
{"Пользователь" if is_admin != 1 else "Админ"}

📅 Дата регистрации:
{created_at}

━━━━━━━━━━━━━━━
'''
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(caption, reply_markup=admin_back_kb)
    else:
        await target.answer(caption, reply_markup=admin_back_kb)

async def admin_make_admin(
    target: Message | CallbackQuery,
    id=None,
):
    user_id = id

    await db.execute(
        '''
        UPDATE users
        SET is_admin = 1
        WHERE id = (?)
        ''',
        (user_id,)
    )

    await db.commit()

    if isinstance(target, CallbackQuery):
        await target.message.edit_text("Админ успешно добавлен.", reply_markup=admin_back_kb_2)
    else:
        await target.answer('Админ успешно добавлен.', reply_markup=admin_back_kb_2)

async def admin_delete_user(

    target: Message | CallbackQuery,
    id=None,
):
    user_id = id

    await db.execute(
        '''
        DELETE
        FROM users
        WHERE id = ?
        ''',
        (user_id,)
    )
    await db.commit()

    if isinstance(target, CallbackQuery):
        await target.message.edit_text("Пользователь успешно удален.", reply_markup=admin_back_kb_2)
    else:
        await target.answer('Пользователь успешно удален.', reply_markup=admin_back_kb_2)


async def admin_give_task(
    target: Message | CallbackQuery,
    id=None,
    user_title=None,
    user_description=None,
    user_materials=None,
    user_deadline=None
):
    caption = f"""
📋 Проверьте данные:

📌 Название: {user_title}
📝 Описание: {user_description}
📎 Материалы: {user_materials}
📅 Дедлайн: {user_deadline}
"""

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(caption, reply_markup=admin_confirm_kb)
    else:
        await target.answer(caption, reply_markup=admin_confirm_kb)

async def admin_confirm_task(
    target: Message | CallbackQuery,
    id=None,
    user_title=None,
    user_description=None,
    user_materials=None,
    user_deadline=None,

):
    
    result = await db.execute(
        '''
        SELECT telegram_id
        FROM users
        WHERE id = ?
        ''',
        (id, )
    )
    res = await result.fetchone()
    user_id = res[0]

    await db.execute(
        '''
        INSERT INTO tasks
        (title, description, assigned_to, created_by, materials, deadline)
        values (?, ?, ?, ?, ?, ?)
        ''',
        (user_title, user_description, user_id, target.from_user.id, user_materials, user_deadline)
    )

    await db.commit()

    if isinstance(target, CallbackQuery):
        await target.message.edit_text("Вы успешно отправили задачу.", reply_markup=admin_back_kb_2)
    else:
        await target.answer("Вы успешно отправили задачу.", reply_markup=admin_back_kb_2)