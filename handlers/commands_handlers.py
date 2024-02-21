from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from config import DB_NAME, admins
from keyboards.admin_inline_keyboards import make_category_list

from states.admin_states import ProductStates, CategoryStates, editProductStates, DELPRO
from utils.database import Database
from utils.my_commands import commands_admin, commands_user

commands_router = Router()
db = Database(DB_NAME)


@commands_router.message(CommandStart())
async def start_handler(message: Message):
    if message.from_user.id in admins:
        await message.bot.set_my_commands(commands=commands_admin)
        await message.answer("Welcome admin, please choose command from commands list")
    else:
        await message.bot.set_my_commands(commands=commands_user)
        await message.answer("Let's start registration")


@commands_router.message(Command('cancel'))
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("All actions canceled, you may continue sending commands")


# With this handler admin can add new category
@commands_router.message(Command('new_category'))
async def new_category_handler(message: Message, state: FSMContext):
    await state.set_state(CategoryStates.newCategory_state)
    await message.answer("Please, send new category name ...")


# Functions for editing category name
@commands_router.message(Command('edit_category'))
async def edit_category_handler(message: Message, state: FSMContext):
    await state.set_state(CategoryStates.updCategory_state_list)
    await message.answer(
        text="Choose category name which you want to change...",
        reply_markup=make_category_list()
    )


@commands_router.callback_query(CategoryStates.updCategory_state_list)
async def callback_category_edit(callback: CallbackQuery, state: FSMContext):
    await state.update_data(cat_name=callback.data)
    await state.set_state(CategoryStates.updCategory_state_new)
    await callback.message.answer(f"Please, send new name for category '{callback.data}'")
    await callback.message.delete()


@commands_router.message(CategoryStates.updCategory_state_new)
async def set_new_category_name(message: Message, state: FSMContext):
    new_cat = message.text
    st_data = await state.get_data()
    old_cat = st_data.get('cat_name')
    res = db.upd_category(message.text, old_cat)
    if res['status']:
        await message.answer("Category name successfully changed")
        await state.clear()
    elif res['desc'] == 'exists':
        await message.reply("This category already exists.\n"
                            "Please, send other name or click /cancel")
    else:
        await message.reply(res['desc'])

# Delete category commad
@commands_router.message(Command('del_category'))
async def del_category(message: Message, state: FSMContext):
    await message.answer('Choose category name for delete')
    await state.set_state(CategoryStates.delCategory_state)

@commands_router.message(CategoryStates.delCategory_state)
async def input_category_name(message: Message, state: FSMContext):
    category_name = message.text
    db.del_category(category_name)
    await message.reply('🚮 DELETE CATEGORY')
    await state.clear()

# ADD PRODUCTS
@commands_router.message(Command('new_product'))
async def new_product(message: Message, state: FSMContext):
    await message.answer('Product name_')
    await state.set_state(ProductStates.name_Product)

@commands_router.message(ProductStates.name_Product)
async def pro_name(message: Message, state: FSMContext):
    name = message.text
    await state.update_data(pro_name = name)
    await message.answer('Image (.JPG, .IMG)')

    await state.set_state(ProductStates.image_Product)

@commands_router.message(ProductStates.image_Product)
async def pro_image(message: Message, state: FSMContext):
    image = message.photo
    if image:
        image_id = image[-1].file_id
        await state.update_data(image = image_id)
        await message.answer('Product IN CATEGORY name')

        await state.set_state(ProductStates.category_Product)
    else:
        await message.answer('Please, send me Photo')

@commands_router.message(ProductStates.category_Product)
async def pro_category(message: Message, state: FSMContext):
    pro_cate = message.text
    st_data = await state.get_data()
    pro_name = st_data.get('pro_name')
    pro_image = st_data.get('image')

    db.add_product(pro_name, pro_image, pro_cate)
    await message.answer("ADD PRODCUT")
    await state.clear()



# EDIT PRODUCT

@commands_router.message(Command('edit_product'))
async def edit_product(message: Message, state: FSMContext):
    await message.answer("Product ID")
    await state.set_state(editProductStates.id_Product)

@commands_router.message(editProductStates.id_Product)
async def get_id(message: Message, state: FSMContext):
    id_pro = message.text
    await state.update_data(id = id_pro)
    await message.answer('Product: new name')
    await state.set_state(editProductStates.name_Product)


@commands_router.message(editProductStates.name_Product)
async def pro_name(message: Message, state: FSMContext):
    name = message.text
    await state.update_data(pro_name = name)
    await message.answer('Image (.JPG, .IMG)')

    await state.set_state(editProductStates.image_Product)

@commands_router.message(editProductStates.image_Product)
async def pro_image(message: Message, state: FSMContext):
    image = message.photo
    if image:
        image_id = image[-1].file_id
        await state.update_data(image = image_id)
        await message.answer('Product IN CATEGORY name')

        await state.set_state(editProductStates.category_Product)
    else:
        await message.answer('Please, send me Photo')

@commands_router.message(editProductStates.category_Product)
async def pro_category(message: Message, state: FSMContext):
    pro_cate = message.text
    try:
        st_data = await state.get_data()
        pro_id = st_data.get('id')
        pro_name = st_data.get('pro_name')
        pro_image = st_data.get('image')

        db.edit_product(pro_id, pro_name, pro_image, pro_cate)
        await message.answer("✅ EDIT PRODCUT")
        await state.clear()
    except:
        await message.answer('⛔ ERROR click -> /cancel')

# DELETE PRODUCTS

@commands_router.message(Command('del_product'))
async def del_pro_command(message: Message, state: FSMContext):
    await message.answer("PRODCUT ID")
    await state.set_state(DELPRO.id_Product)

@commands_router.message(DELPRO.id_Product)
async def del_pro(message: Message, state: FSMContext):
    pro_id = message.text
    db.del_product(pro_id)
    await message.answer('🚮 DELETE PRODCUT')
    await state.clear()