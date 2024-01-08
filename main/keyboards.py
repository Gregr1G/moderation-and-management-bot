from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def roles_kb(items: list):
    keys = [KeyboardButton(text=item) for item in items]

    return ReplyKeyboardMarkup(keyboard=[keys], resize_keyboard=True)

def col_kb(items: list):
    keys = [[KeyboardButton(text=item)] for item in items]

    return ReplyKeyboardMarkup(keyboard=keys, resize_keyboard=True)