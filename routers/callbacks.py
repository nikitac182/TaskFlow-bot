import aiogram
import aiosqlite

from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from const import *
from keyboards import *
from states.user_state import WithDrawState

from routers.user import render_task_description, render_tasks_page, render_submission_menu

router = aiogram.Router()

bot: aiogram.Bot | None = None
db: aiosqlite.Connection | None = None

@router.callback_query()
async def callbacks(callback: CallbackQuery, state: FSMContext) -> None: 

    data = callback.data
    state_data = await state.get_data()
    current_page: int = state_data.get('current_page', 0)
    current_task_id: int = state_data.get('task_id', 0)

    if data.startswith('task_data_'):
        task_id = int(data.split('_')[-1])
        await state.update_data(task_id=task_id)
        await render_task_description(callback, task_id)

    elif data == 'p_back':
        await render_tasks_page(callback, page=current_page)

    elif data == 'p_back_2':
        await render_task_description(callback, task_id=current_task_id)

    elif data.startswith('page_') or data.startswith('back_'):
        page = int(data.split('_')[-1])
        await state.update_data(current_page=page)
        await render_tasks_page(callback, page=page)

    elif data == 'make_task':
        await render_submission_menu(callback)
        await state.set_state(WithDrawState.request)

    elif data == 'k':
        await callback.message.edit_text("123")
    
    await callback.answer()
