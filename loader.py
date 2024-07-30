from aiogram import Dispatcher , Router, Bot
from aiogram.enums import ParseMode
from database.db_movies import Database_Movies
from database.db_user import Database_Users
from aiogram.client.default import DefaultBotProperties

TOKEN = "6769519460:AAHpks5wgRnyF2e8zlr7EBb6MbjeRKJL9EE"

db_movies = Database_Movies()
db_user = Database_Users()
dp = Dispatcher()
router_admin = Router()
router_user = Router()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp.include_router(router=router_admin)
dp.include_router(router=router_user)
