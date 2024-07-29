from aiogram import Dispatcher , Router, Bot
from aiogram.enums import ParseMode
from database.db_admin import Database_Product
from database.db_user import Database_Users

TOKEN = "YOUR_TOKEN"

db_admin = Database_Admins()
db_user = Database_Users()
dp = Dispatcher()
router_admin = Router()
router_user = Router()
bot = Bot(token=TOKEN)
dp.include_router(router=router_admin)
dp.include_router(router=router_user)
