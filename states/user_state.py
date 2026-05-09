from aiogram.fsm.state import State, StatesGroup

class WithDrawState(StatesGroup):
    request = State()
