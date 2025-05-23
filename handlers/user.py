from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram import F
from loader import router_user, bot
from database.db_movies import *
from database.db_user import *
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.markdown import text


@router_user.message(CommandStart())
async def start(msg: Message):
    full_name = msg.from_user.full_name
    username = msg.from_user.username or ''
    user_id = msg.from_user.id

    user = await select_user(user_id)
    if not user:
        await add_user(user_id, full_name, username)

    # await bot.send_animation(chat_id=user_id, animation='CgACAgIAAxkBAAIBrGaoxqBqE4YW9A9LscFaIYZMG2h5AAI1TgACiWhJSXDiMTkMyvYjNQQ')
    await msg.answer(f"Assalomu aleykum {msg.from_user.full_name}!😊")
    await check_subscription(msg)


async def check_subscription(message: Message):
    channel_ids = ["@chanel_username"]  # Kanal username'lari yoki ID'lari
    channel_urls = {
        "@chanel_username": "https://t.me/chanel_link",
    }
    user_id = message.from_user.id
    subscribed_channels = set()  # Obuna bo'lgan kanallar ro'yxati

    # Har bir kanalni tekshirib chiqamiz
    for channel_id in channel_ids:
        try:
            member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member.status != 'left':
                subscribed_channels.add(channel_id)  # Obuna bo'lgan kanallar ro'yxatiga qo'shamiz
        except Exception as e:
            print(f"Kanal tekshirishda xatolik: {channel_id} - {e}")

    # Obuna bo'lmagan kanallarni aniqlaymiz
    not_subscribed_channels = set(channel_ids) - subscribed_channels

    # `inline_keyboard` ro'yxatini yaratamiz
    inline_keyboard = []

    for channel_id in not_subscribed_channels:
        inline_keyboard.append([InlineKeyboardButton(text=f"{channel_id[1:]}", url=channel_urls[channel_id])])

    markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    if not_subscribed_channels:
        await message.answer(
            "Iltimos, quyidagi kanallarga obuna bo‘ling. Obunadan so‘ng /start buyrug‘ini yuboring.👇🏻",
            reply_markup=markup
        )
    else:
        await message.answer("Kino kodini yuboring: ✍️")

@router_user.message()
async def check_user(msg: Message):
    await check_users(msg)

async def check_users(message: Message):
    channel_id = "@chanel_username"
    user_id = message.from_user.id
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        if member.status != 'left':
            movie_code = message.text
            movie = await get_movie_by_code(movie_code)
            
            if movie:
                if movie.get('movi_vd'):  # `movi_vd` mavjudligini tekshirib ko'ramiz
                    await bot.send_video(
                        chat_id=user_id,
                        video=movie['movi_vd'],
                        caption=f"🎬Kino: <b>{movie['movi_name']}</b>\n📌Kod: <b>{movie['movi_code']}</b>\n\n🤖 Bot: @bot_username"
                    )
            else:
                await message.answer("Bunday kod mavjud emas!")
        else:
            await message.answer(
                "<b>Kanallarga obuna bo'lishingizni so'raymiz.</b>\n<b>A'zo bo'lganingizdan so'ng</b> /start <b>buyrug'ini yuboring</b>",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="1-kanal", url="https://t.me/chanel_link")]
                    ]
                )
            )
    except Exception as e:
        print("Xatolik sodir bo'ldi:", e)
        await message.answer("Uzr, qandaydir xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")