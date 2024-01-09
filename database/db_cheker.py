# import asyncio
# import schedule
# import datetime
# from aiogram import Bot
# import os
# from dotenv import load_dotenv
# from database.DbBot import Dbbot
#
# load_dotenv()
# bot = Bot(token=os.getenv('TOKEN'))
# db = Dbbot("")

# async def clean():
#     delete_time = datetime.datetime.now() - datetime.timedelta(minutes=1)
#     for user in db.reader("users"):
#         if sum(user[5:]) <= 0 and user[1] < delete_time:
#             print(user[2])
#             try:
#                 await bot.ban_chat_member(os.getenv("CHAT_ID"), user[2])
#             except Exception as e:
#                 print(e)
#     else:
#         print("No one to clean")
#
# async def main():
#     schedule.every(1).minutes.do(clean)
#
#     while True:
#         schedule.run_pending()
#         await asyncio.sleep(1)
#
# if __name__ == "__main__":
#     main()
