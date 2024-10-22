import asyncio
import logging
import sys

from loader import dp, bot, db_movies, db_user
import handlers

async def main():
    await dp.start_polling(bot)
    db_movies.close()
    db_user.close()
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())