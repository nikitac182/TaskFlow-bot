from aiogram.fsm.state import State, StatesGroup

class WithDrawState(StatesGroup):
    amount = State()
    number = State()
