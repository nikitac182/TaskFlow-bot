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

from states.admin_state import AdminStates
from const import *
from keyboards import *
from states.user_state import WithDrawState

from routers.user import (
    render_task_description,
    render_tasks_page,
    render_submission_menu
    )

from routers.admin import (
    render_admin_page,
    render_admin_zone_menu,
    render_user_full_info,
    admin_make_admin,
    admin_delete_user,
)

router = aiogram.Router()

bot: aiogram.Bot | None = None
db: aiosqlite.Connection | None = None

@router.callback_query()
async def callbacks(callback: CallbackQuery, state: FSMContext) -> None: 

    data = callback.data
    state_data = await state.get_data()
    current_page: int = state_data.get('current_page', 0)
    current_task_id: int = state_data.get('task_id', 0)
    admin_page: int = state_data.get('admin_page', 0)
    id: int = state_data.get('id', 0)

    if data.startswith('task_data_'):
        task_id = int(data.split('_')[-1])
        await state.update_data(task_id=task_id)
        await render_task_description(callback, task_id)

    elif data == 'p_back':
        await render_tasks_page(callback, page=current_page)

    elif data == 'p_back_2':
        await render_task_description(callback, task_id=current_task_id)

    elif data.startswith('next_page_') or data.startswith('back_page_'):
        page = int(data.split('_')[-1])
        await state.update_data(admin_page=page)
        await render_admin_page(
            target=callback,
            page=page,
        )

    elif data == 'back_admin':
        await render_admin_zone_menu(callback)

    elif data.startswith('page_') or data.startswith('back_'):
        page = int(data.split('_')[-1])
        await state.update_data(current_page=page)
        await render_tasks_page(callback, page=page)

    elif data == 'make_task':
        await render_submission_menu(callback)
        await state.set_state(WithDrawState.request)

    elif data == 'open_user':
        await callback.message.answer("Введите id пользователя")
        await state.set_state(AdminStates.waiting_for_id)

    elif data == 'admin_users_menu':
        await render_admin_page(target=callback)
    
    elif data == 'admin_users_back':
        await render_admin_page(target=callback, page=admin_page)

    elif data == 'admin_make_admin':
        await admin_make_admin(target=callback, id=id)

    elif data =='admin_delete_user':
        await admin_delete_user(target=callback, id=id)

    await callback.answer()

@router.message(AdminStates.waiting_for_id)
async def show_user_info(message: Message, state: FSMContext):

    user_id = int(message.text)

    await state.update_data(id=user_id)
    await state.set_state(None)
    await render_user_full_info(
        target=message,
        id=user_id
    )