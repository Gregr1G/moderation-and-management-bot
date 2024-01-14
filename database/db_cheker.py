from aiogram import Bot
import datetime
from database.DbBot import Dbbot
import os
from dotenv import load_dotenv

load_dotenv()
Database = Dbbot('localhost',3306,'root','1234','hui')

async def clean(bot: Bot):

    delete_time = datetime.datetime.now() - datetime.timedelta(minutes=20)

    for user in Database.reader("users"):
        if sum(user[5:]) <= 0 and user[1] < delete_time:
            print(user[2])
            try:
                await bot.ban_chat_member(os.getenv("CHAT_ID"), user[2])
            except Exception as e:
                print(e)
    else:
        print("No one to clean")