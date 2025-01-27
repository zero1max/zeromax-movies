import asyncio
import logging
import sys

from database.db_movies import setup_movie
from database.db_user import setup_user
from loader import dp, bot
import handlers

async def main():
    await dp.start_polling(bot)
    await setup_movie()
    await setup_user()
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())