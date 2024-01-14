import asyncio
import datetime

from aiogram import Bot, Dispatcher, Router, F

from dotenv import load_dotenv

from database.DbBot import Dbbot
from database.db_cheker import clean
from supmodules.helpmodule import *

from apscheduler.schedulers.asyncio import AsyncIOScheduler



from aiogram.fsm.context import FSMContext
from keyboards import roles_kb, col_kb

from states import Newmember, Tag, Table
from filters.filters import ChatTypeFilter

from aiogram.filters import ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER, Command
import os


"""Подключение к базе данных"""
Database = Dbbot('localhost',3306,'root','1234','hui')

"""Создание экземпляра бота"""
load_dotenv()
bot = Bot(os.getenv('TOKEN'))
router = Router()



"""Получение данных нового пользователя""" # добавить фильтр для лс
@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def get_new_member(message: types.ChatMemberUpdated):

    usr = dict(message.new_chat_member.user)

    if not(Database.check_or_get("user_id", "user_id", usr["id"])):


        Database.add_to_table('users', [0,
                                        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                        usr["id"],
                                        f"@{usr['username']}",
                                        message.from_user.first_name])


    await bot.send_message(usr["id"], "Напиши команду /roles чтобы выбрать или изменить роли. \n"
                                      "Вы будете удалены если не выберите роли.", reply_markup=roles_kb(["/roles"]))

@router.message(Command("roles"), ChatTypeFilter(chat_type=["private"]))
async def start_reg(message: types.Message, state: FSMContext):
    await message.answer(f"Напиши роли из списка: {' '.join(Database.cols_list('users')[5:])}\nПример: role1 role2 role10", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Newmember.roles)

@router.message(Newmember.roles)
async def get_roles(message: types.Message, state: FSMContext):
    if set(message.text.split()).issubset(Database.cols_list('users')[5:]):
        await message.answer("Подтвердить?", reply_markup=roles_kb(["Да", "Отмена"]))
        await state.update_data(roles=message.text.split())

        await state.set_state(Newmember.addindb)
    else:
        await message.answer(f"Вы где-то ошиблись.\nВаше сообщение: {message.text}")


@router.message(Newmember.addindb, F.text.in_(["Да", "Отмена"]))
async def addindatabase(message: types.Message, state: FSMContext):
    await message.answer("Принято", reply_markup=types.ReplyKeyboardRemove())

    if message.text == "Отмена":
        await state.clear()

        return

    data = await state.get_data()
    await state.clear()

    if "roles" in data and bool(Database.check_or_get("user_id", "user_id", message.from_user.id)):
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
    else:
        await message.answer("Не понимаю")

@router.message(Tag.roles_to_tag)
async def get_message(message: types.Message, state: FSMContext):
    await message.answer("Перешлите сообщение на которое нужно тэгнуть")
    await state.update_data(roles_to_tag=list(set(Database.check_or_get("username", f"{tag}", 1) for tag in message.text.split())))
    await state.set_state(Tag.send_fin_message)

@router.message(Tag.send_fin_message, ChatTypeFilter(chat_type=["private"]))
async def sendmessage(message: types.Message, state: FSMContext):
    tag_list = await state.get_data()
    await state.clear()

    if not tag_list:
        return

    tags = lol([item[0] for item in tag_list['roles_to_tag'][0]], 50)


    for tag in tags:

        if message.text:
            await bot.send_message(os.getenv("CHAT_ID"), f"{message.text}\n{' '.join(tag)}")

        if message.caption:
            await message.copy_to(os.getenv("CHAT_ID"), caption=f"{message.caption}\n{' '.join(tag)}")




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
    else:
        await message.answer("Не понимаю")


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
    functions = ["Прочитать", "Добавить"]

    if message.from_user.id == int(os.getenv("ADMINID")):
        functions += ["Редактирование", "Удаление"]

    await message.answer(f"Что хотите сделать?", reply_markup=roles_kb(functions))
    await state.update_data(table_name=message.text)
    await state.set_state(Table.mode)

@router.message(Table.mode)
async def get_mode(message: types.Message, state: FSMContext):
    # await state.update_data(mode=message.text)
    data = await state.get_data()

    if data["table_name"] == 'users' and message.from_user.id != int(os.getenv("ADMINID")):
        await message.answer("Не понимаю")
        return


    if message.text == "Прочитать":
        await message.answer('\n'.join([' '.join(map(str, list(item))) for item in Database.reader(data['table_name'])]), reply_markup=types.ReplyKeyboardRemove())
        await state.clear()



    if message.text == "Добавить":
        await message.answer("Напишите данные которые хотите добавить поразрядно.\n"
                             "Пример: 1 0 да нет\n"
                             f"{'|'.join(Database.table_info(data['table_name'])[1:])}")

        await state.set_state(Table.add_data)

    if message.from_user.id == int(os.getenv("ADMINID")):

        if message.text == "Редактирование":
            await message.answer('\n'.join([' '.join(map(str, list(item))) for item in Database.reader(data['table_name'])]))

            await message.answer(f"Чтобы выбрать строку для редактирования напиши через пробел: имя колоки, значение в ряду колонки, новое значение."
                                 
                                 f"\nКолонки{Database.cols_list(data['table_name'])}")
            await state.set_state(Table.edit)

        if message.text == "Удаление":
            await message.answer("Чтобы выбрать строку для уаления напишите id строки")

            await state.set_state(Table.del_data)

@router.message(Table.add_data)
async def add_data(message: types.Message, state: FSMContext):
    data = await state.get_data()

    try:
        Database.add_to_table(data["table_name"], ["0"] + message.text.split())
    except Exception as a:
        print(a)
        await message.answer("Произошла ошибка, возможно вы ошиблись")

    await state.clear()




@router.message(Table.edit)
async def edit(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    try:
        Database.single_update(data["table_name"], message.text.split()[1], message.text.split()[0],message.text.split()[2])
        await message.answer("Данные изменены")
    except Exception:
        await message.answer("Ошибка")



@router.message(Table.del_data)
async def delete(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    if message.text.isdigit():
        Database.deleter("string", data["table_name"], int(message.text))


# @router.message(ChatTypeFilter(chat_type=["group", "supergroup"]))
# async def user_check(message: types.Message):
#     if Database.check_or_get("id", "user_id", f"{message.from_user.id}"):
#         pass
#     else:
#         await bot.restrict_chat_member(message.chat.id, message.from_user.id, permissions=ChatPermissions(can_send_messages=False, can_invite_users=False))
#         await bot.send_message(message.from_user.id, "Выберите роли!!!")


async def main():
    dp = Dispatcher(bot=bot)

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(clean, trigger="interval", minutes=1,kwargs={"bot":bot})
    scheduler.start()

    dp.include_router(router)


    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)




if __name__ == '__main__':
    asyncio.run(main())