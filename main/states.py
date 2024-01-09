from aiogram.fsm.state import StatesGroup, State


class Newmember(StatesGroup):
    roles = State()
    addindb = State()


class Tag(StatesGroup):
    start = State()
    roles_to_tag = State()
    send_fin_message = State()

class Table(StatesGroup):
    table_name = State()
    mode = State()
    add_data = State()
    del_data = State()
    edit = State()