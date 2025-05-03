from aiogram import Dispatcher , Router, Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

TOKEN = "bot_token"

dp = Dispatcher()
router_admin = Router()
router_user = Router()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp.include_router(router=router_admin)
dp.include_router(router=router_user)
