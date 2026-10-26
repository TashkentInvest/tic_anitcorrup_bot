from aiogram.fsm.state import State, StatesGroup


class AppealForm(StatesGroup):
    name = State()
    phone = State()
    district = State()
    department = State()
    subject = State()
    body = State()
    files = State()


class CheckForm(StatesGroup):
    number = State()
