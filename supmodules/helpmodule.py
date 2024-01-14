import prettytable
from aiogram import types
import os

user = ""

admin = ""


def table_former(data, ans):
    a = prettytable.PrettyTable(ans)
    for i in data:
        a.add_row(i)

    return a


def kb_choise(message: types.Message):
    admin_keyboard = ["/tag", "/tables", "/roles"]
    user_keyboard = ["/roles", "/tables"]

    if message.from_user.id == int(os.getenv("ADMINID")):
        return admin_keyboard
    else:
        return user_keyboard

def desc_choise(message: types.Message):
    admin = "--------------------"
    user = "--------------------"

    if message.from_user.id == int(os.getenv("ADMINID")):
        return admin
    else:
        return user

lol = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]



