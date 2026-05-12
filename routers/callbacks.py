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

from states.admin_state import AdminStates, AdminNewStates, AdminTaskStates
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
    admin_give_task,
    admin_confirm_task,
    admin_task_menu,
    admin_open_task,
    admin_confirms_task,
    admin_rejects_task,
)

router = aiogram.Router()

bot: aiogram.Bot | None = None
db: aiosqlite.Connection | None = None

@router.callback_query()
async def callbacks(callback: CallbackQuery, state: FSMContext) -> None: 

    data = callback.data
    state_data = await state.get_data()
    current_page: int = state_data.get('current_page', 0)
    current_task_id: int = state_data.get('current_task_id', 0)
    admin_page: int = state_data.get('admin_page', 0)
    id: int = state_data.get('id', 0)
    user_title = state_data.get('user_title', 0)
    user_description = state_data.get('user_description', 0)
    user_materials = state_data.get('user_materials', 0)
    user_deadline = state_data.get('user_deadline', 0)
    user_id = state_data.get('user_id', 0)

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

    elif data.startswith('task_next_page_') or data.startswith('task_back_page_'):
        page = int(data.split('_')[-1])
        await state.update_data(admin_page=page)
        await admin_task_menu(
            target=callback,
            page=page,
        )

    elif data == 'admin_tasks_menu':
        await admin_task_menu(target=callback)

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

    elif data == 'open_task':
        await callback.message.answer("Введите id задачи")
        await state.set_state(AdminTaskStates.waiting_for_id)

    elif data == 'admin_users_menu':
        await render_admin_page(target=callback)
    
    elif data == 'admin_users_back':
        await render_admin_page(target=callback, page=admin_page)

    elif data == 'admin_make_admin':
        await admin_make_admin(target=callback, id=id)

    elif data == 'admin_delete_user':
        await admin_delete_user(target=callback, id=id)

    elif data == 'admin_task_back':
        await render_admin_zone_menu(target=callback)

    elif data == 'admin_give_task':
        await callback.message.answer("Введите название задачи.")
        await state.set_state(AdminNewStates.waiting_for_title)

    elif data == 'admin_confirm':
        await admin_confirm_task(
            target=callback,
            id=id,
            user_title=user_title,
            user_description=user_description,
            user_materials=user_materials,
            user_deadline=user_deadline
        )
    
    elif data == 'admin_open_task':
        await admin_open_task(
            target=callback,
            id=current_task_id
        )
    
    elif data == 'admin_confirms_task':
        await admin_confirms_task(
            target=callback,
            id=current_task_id
        )
    
    elif data == 'admin_rejects_task':
        await admin_rejects_task(
            target=callback,
            id=current_task_id
        )

@router.message(AdminStates.waiting_for_id)
async def show_user_info(message: Message, state: FSMContext):

    user_id = int(message.text)

    await state.update_data(id=user_id)
    await state.set_state(None)
    await render_user_full_info(
        target=message,
        id=user_id
    )
@router.message(AdminTaskStates.waiting_for_id)
async def show_task_info(message: Message, state: FSMContext):
    
    current_task_id = int(message.text)

    await state.update_data(current_task_id=current_task_id)
    await state.set_state(None)
    await admin_open_task(
        target=message,
        id=current_task_id
    )

@router.message(AdminNewStates.waiting_for_title)
async def get_user_title(message: Message, state: FSMContext):
    user_title = message.text
    await state.update_data(user_title=user_title)
    await message.answer("Введите описание задачи.")
    await state.set_state(AdminNewStates.waiting_for_description)

@router.message(AdminNewStates.waiting_for_description)
async def get_user_description(message: Message, state: FSMContext):
    user_description = message.text
    await state.update_data(user_description=user_description)
    await message.answer("Введите материалы к задаче.")
    await state.set_state(AdminNewStates.waiting_for_materials)

@router.message(AdminNewStates.waiting_for_materials)
async def get_user_materials(message: Message, state: FSMContext):
    user_materials = message.text
    await state.update_data(user_materials=user_materials)
    await message.answer("Введите дедлайн к задаче.")
    await state.set_state(AdminNewStates.waiting_for_deadline)

@router.message(AdminNewStates.waiting_for_deadline)
async def get_user_deadline(message: Message, state: FSMContext):
    user_deadline = message.text
    await state.update_data(user_deadline=user_deadline)
    data = await state.get_data()
    user_title = data.get('user_title', 0)
    id = data.get('id', 0)
    user_description = data.get('user_description', 0)
    user_materials = data.get('user_materials', 0)
    await admin_give_task(
            target=message,
            id=id,
            user_title=user_title,
            user_description=user_description,
            user_materials=user_materials,
            user_deadline=user_deadline
        )
    await state.set_state(None)