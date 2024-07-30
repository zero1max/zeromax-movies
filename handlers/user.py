from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram import F
from loader import router_user, bot, db_movies, db_user
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

@router_user.message(CommandStart())
async def start(msg: Message):
    full_name = msg.from_user.full_name
    surname = msg.from_user.last_name or ''
    user_id = msg.from_user.id
    
    db_user.create_table()
    db_user.add_user(user_id, full_name, surname)
    await msg.answer(f"Assalomu aleykum {msg.from_user.full_name}!😊")
    await check_subscription(msg)

async def check_subscription(message: Message):
    channel_id = "CHANNEL_ID"
    user_id = message.from_user.id
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        if member.status != 'left':
            await message.answer("Kino kodini yuboring: ✍️")
        else:
            await message.answer(
                "Kanallarga obuna bo'lishingizni so'raymiz.\nA'zo bo'lganingizdan so'ng /start buyrug'ini yuboring",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(text="A'zo bo'lish", url="https://t.me/CHANNEL")]]
                )
            )
    except Exception as e:
        print("Xatolik sodir bo'ldi:", e)
        await message.answer("Uzr, qandaydir xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")

@router_user.message()
async def check_user(msg: Message):
    await check_users(msg)

async def check_users(message: Message):
    channel_id = "CHANNEL_ID" 
    user_id = message.from_user.id
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        if member.status != 'left':
            movie_code = message.text
            movie = db_movies.get_movie_by_code(movie_code)
            
            if movie:
                if movie['movi_vd']:
                    await bot.send_video(chat_id=user_id, video=movie['movi_vd'], caption=f"🎬Kino: <b>{movie['movi_name']}</b>\n📌Kod: <b>{movie['movi_code']}</b>\n\n🤖 Bot: @zeromaxs_movies_bot")
            else:
                await message.answer("Bunday kod mavjud emas!")
        else:
            await message.answer(
                "<b>Kanallarga obuna bo'lishingizni so'raymiz.</b>\n<b>A'zo bo'lganingizdan so'ng</b> /start <b>buyrug'ini yuboring</b>",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(text="A'zo bo'lish", url="https://t.me/channel")]]
                )
            )
    except Exception as e:
        print("Xatolik sodir bo'ldi:", e)
        await message.answer("Uzr, qandaydir xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")