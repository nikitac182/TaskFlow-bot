from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

class WithDrawState(StatesGroup):
    amount = State()
    number = State()
