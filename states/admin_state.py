from aiogram.fsm.state import State, StatesGroup

class AddBalanceState(StatesGroup):
    amount = State()
    id = State()

class ReduceBalanceState(StatesGroup):
    amount = State()
    id = State()

class AdminStates(StatesGroup):
    waiting_for_id = State()

class AdminTaskStates(StatesGroup):
    waiting_for_id = State()

class AdminNewStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_materials = State()
    waiting_for_deadline = State()