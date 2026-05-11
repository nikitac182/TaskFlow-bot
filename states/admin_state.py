from aiogram.fsm.state import State, StatesGroup

class AddBalanceState(StatesGroup):
    amount = State()
    id = State()

class ReduceBalanceState(StatesGroup):
    amount = State()
    id = State()

class AdminStates(StatesGroup):
    waiting_for_id = State()