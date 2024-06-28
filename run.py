import asyncio
import os
import logging
from dotenv import load_dotenv, find_dotenv



from aiogram import *



load_dotenv(find_dotenv())

TOKEN = os.getenv('TOKEN')

bot = Bot(token = TOKEN)
dp = Dispatcher()



async def main():
    dp.include_router(router)
    await dp.start_polling(bot)




if __name__ == '__main__':
    from app.handlers import router
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('exit')