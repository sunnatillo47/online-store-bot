from aiogram.fsm.state import State, StatesGroup


class CategoryStates(StatesGroup):
    newCategory_state = State()
    updCategory_state_list = State()
    updCategory_state_new = State()
    delCategory_state = State()

class ProductStates(StatesGroup):
    name_Product = State()
    image_Product = State()
    category_Product = State()

class editProductStates(StatesGroup):
    id_Product = State()
    name_Product = State()
    image_Product = State()
    category_Product = State()

class DELPRO(StatesGroup):
    id_Product = State()