from aiogram.fsm.state import State, StatesGroup


class States(StatesGroup):
    start = State()
    upload_photo = State()
    choose_option = State()
    show_result = State()
