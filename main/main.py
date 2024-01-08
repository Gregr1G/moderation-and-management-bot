import asyncio
import datetime

from aiogram import Dispatcher, types, Router, F

from dotenv import load_dotenv
from database.DbBot import Dbbot
from database.db_cheker import bot
from aiogram.fsm.context import FSMContext
from keyboards import roles_kb, col_kb

from states import Newmember, Tag, Table
from filters.filters import ChatTypeFilter

from aiogram.filters import ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER, Command
import os


"""Подключение к базе данных"""
Database = Dbbot("")

"""Создание экземпляра бота"""
load_dotenv()
# bot = Bot(os.getenv('TOKEN'))
router = Router()



"""Получение данных нового пользователя""" # добавить фильтр для лс
@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def get_new_member(message: types.ChatMemberUpdated):

    usr = dict(message.new_chat_member.user)
    usr["id"] = 1055854958
    await bot.send_message(usr["id"], "Напиши команду /roles чтобы выбрать или изменить роли.", reply_markup=roles_kb(["/roles"]))

@router.message(Command("roles"), ChatTypeFilter(chat_type=["private"]))
async def start_reg(message: types.Message, state: FSMContext):
    await message.answer(f"Напиши роли из списка: {' '.join(Database.cols_list('users')[5:])}\nПример: role1 role2 role10", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Newmember.roles)

@router.message(Newmember.roles)    # F.text.in_(Database.cols_list('users')[5:]+["Готово"])
async def get_roles(message: types.Message, state: FSMContext):
    if set(message.text.split()).issubset(Database.cols_list('users')[5:]):
        await message.answer("Подтвердить?", reply_markup=roles_kb(["Да", "Нет"]))
        await state.update_data(roles=message.text.split())

        await state.set_state(Newmember.addindb)
    else:
        await message.answer(f"Вы где-то ошиблись.\nВаше сообщение: {message.text}")


@router.message(Newmember.addindb, F.text.in_(["Да", "Нет"]))
async def addindatabase(message: types.Message, state: FSMContext):
    await message.answer("Принято", reply_markup=types.ReplyKeyboardRemove())

    if message.text == "Нет":
        await state.clear()
        return

    if not(Database.check_or_get("user_id", "user_id", message.from_user.id)):


        await state.update_data(addindatabase=[0,
                                               datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                               message.from_user.id,
                                               f"@{message.from_user.username}",
                                               message.from_user.first_name])

    data = await state.get_data()
    await state.clear()

    if "addindatabase" in data:
        Database.add_to_table('users', data["addindatabase"])

    if "roles" in data:
        update_query = Database.cols_list("users")[5:]

        for i in range(len(update_query)):
            if update_query[i] not in data["roles"]:
                update_query[i] = 0

            else:
                update_query[i] = 1
        update_query = ["-" for _ in range(5)] + update_query

        Database.update_data_in_table("users", message.from_user.id, "user_id", update_query)


"""Хэндлеры для управления базой данных"""

"""Админ"""
# тэг участников по ролям
@router.message(Command("tag"), ChatTypeFilter(chat_type=["private"]))
async def get_tag_roles(message: types.Message, state: FSMContext):
    if message.from_user.id == int(os.getenv("ADMINID")):
        await message.answer(f"Напишите роли для тэга через пробел.\n"
                             f"Роли на данный момент: {' '.join(Database.cols_list('users')[5:])}")
        await state.set_state(Tag.roles_to_tag)

@router.message(Tag.roles_to_tag)
async def get_message(message: types.Message, state: FSMContext):
    await message.answer("Перешлите сообщение на которое нужно тэгнуть")
    await state.update_data(roles_to_tag=list(set(Database.check_or_get("username", f"{tag}", 1) for tag in message.text.split())))
    await state.set_state(Tag.send_fin_message)

@router.message(Tag.send_fin_message, ChatTypeFilter(chat_type=["private"]))
async def sendmessage(message: types.Message, state: FSMContext):
    tag_list = await state.get_data()


    if tag_list:
        text = ""

        if message.text:
            text += message.text
        if message.caption:
            text += message.caption
        # добавить цикл
        await message.copy_to(os.getenv("CHAT_ID"), caption=f"{text}\n{' '.join([item[0] for item in  tag_list['roles_to_tag'][0]])}")
    await state.clear()

# добавление и удаление колонок ролей
@router.message(Command(commands=["addroles", "delroles"]), ChatTypeFilter(chat_type=["private"]))
async def roles_manage(message: types.Message):
    if message.from_user.id == int(os.getenv("ADMINID")):
        start_command, *args = message.text.split()

        func = Database.cons_cols

        if start_command == "/delroles":
            func = Database.del_cols

        for i in args:
            func(i)

        await message.answer(f"Роли на данный момент: {Database.cols_list('users')[5:]}")

"""Управление таблицами"""
@router.message(Command("tables"), ChatTypeFilter(chat_type=["private"]))
async def tables(message: types.Message, state: FSMContext):
    tables = [item[0] for item in Database.list_of_tables()]

    if message.from_user.id != int(os.getenv("ADMINID")):
        tables.remove("users")

    await message.answer(f"Выберите нужную таблицу", reply_markup=col_kb(tables))

    await state.set_state(Table.table_name)


@router.message(Table.table_name)
async def send_table(message: types.Message, state: FSMContext):
    # datalist = Database.reader(message.text)
    # ans = Database.cols_list(message.text)

    await message.answer(f"Что хотите сделать?", reply_markup=roles_kb(["Прочитать", "Добавить"]))
    await state.update_data(table_name=message.text)
    await state.set_state(Table.mode)

@router.message(Table.mode)
async def get_mode(message: types.Message, state: FSMContext):
    # await state.update_data(mode=message.text)
    data = await state.get_data()
    if message.text == "Прочитать":
        await message.answer('\n'.join([' '.join(map(str, list(item))) for item in Database.reader(data['table_name'])]), reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
    else:
        await message.answer("Напишите данные которые хотите добавить поразрядно.\n"
                             "Пример: 1 0 да нет\n"
                             f"{'|'.join(Database.cols_list(data['table_name'])[1:])}")
        await state.set_state(Table.add_data)

@router.message(Table.add_data)
async def add_data(message: types.Message, state: FSMContext):
    data = await state.get_data()

    try:
        Database.add_to_table(data["table_name"], ["0"] + message.text.split())
    except Exception as a:
        print(a)
        await message.answer("Произошла ошибка, возможно вы ошиблись")

    await state.clear()


@router.message()
async def user_check(message: types.Message):
    if message.chat.type != "private":
        if Database.check_or_get("id", "user_id",f"{message.from_user.id}"):
            pass
        else:
            await bot.ban_chat_member(message.chat.id, message.from_user.id)

async def main():
    dp = Dispatcher(bot=bot)
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())