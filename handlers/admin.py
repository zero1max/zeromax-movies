from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command, Filter, StateFilter
from aiogram import F
from loader import bot, router_admin
from database.db_movies import *
from database.db_user import *
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.defoult.defoult_key import *
from keyboards.inline.inline_key import *
from aiogram.types.input_file import FSInputFile
from aiogram.enums import ChatAction

class Movies(StatesGroup):
    movi_code = State()
    movi_name = State()
    movi_vd = State()

class BroadcastStates(StatesGroup):
    waiting_for_broadcast_type = State()
    waiting_for_message = State()
    waiting_for_caption = State()

class Admin(Filter):
    def __init__(self, admin_id: int):
        self.admin_id = admin_id

    async def __call__(self, msg: Message):
        return msg.from_user.id == self.admin_id

ADMIN_ID = "ADMIN_ID"

# ----------------------------------- START --------------------------------
@router_admin.message(CommandStart(), Admin(ADMIN_ID))
async def start(msg: Message):
    await msg.answer("Assalomu aleykum Admin!\n\nBuyruqlar:\n/id - ID olish\n/broadcast - Userlarda xabar yuborish\n/get_db - sqlite ni olish", reply_markup=menu_admin)

# ----------------------------------- Sqlite olish --------------------------------
@router_admin.message(Command('get_db'))
async def get_db(msg: Message, action=ChatAction.UPLOAD_DOCUMENT):
    db_path = './movies.db'
    database = FSInputFile(db_path)

    await bot.send_document(chat_id=ADMIN_ID, document=database)

# ----------------------------------- All movies --------------------------------
@router_admin.message(F.text == 'Barcha kinolar')
async def all_movies(msg: Message):
    movies = await select_movies()
    movies_list = [f"Kino IDsi: <b>{movie[0]}</b>, Kino kodi va nomi: <b>{movie[1]} - {movie[2]}</b>" for movie in movies]
    
    movies_str = ""
    for movie in movies_list:
        if len(movies_str) + len(movie) > 4000: 
            await msg.answer(movies_str, reply_markup=menu_admin)
            movies_str = ""  
        movies_str += movie + "\n"
    
    if movies_str: 
        await msg.answer(movies_str, reply_markup=menu_admin)

# ----------------------------------- ADD movies --------------------------------

@router_admin.message(F.text == 'Yangi kino qo\'shish')
async def add_movi_code(msg: Message, state: FSMContext):
    await state.set_state(Movies.movi_code)
    await msg.answer("Kino kodini yuboring!")

@router_admin.message(Movies.movi_code)
async def movi_code_set(msg: Message, state: FSMContext):
    movi_code = msg.html_text
    movie = await get_movie_by_code(movi_code)
    
    if movie:
        await msg.answer(f"Bunday kino allaqachon mavjud!\n\nKino kodi: {movie['movi_code']}\nKino nomi: {movie['movi_name']}")
        await state.clear()
    else:
        await state.update_data(movi_code=movi_code)
        await state.set_state(Movies.movi_name)
        await msg.answer("Kino nomini yuboring!")

@router_admin.message(Movies.movi_name)
async def movi_name_set(msg: Message, state: FSMContext):
    await state.update_data(movi_name=msg.text)
    await state.set_state(Movies.movi_vd)
    await msg.answer("Kino videosini yuboring!")

@router_admin.message(Movies.movi_vd)
async def movi_vd_set(msg: Message, state: FSMContext):
    await state.update_data(movi_vd=msg.video.file_id)
    data = await state.get_data()
    print(data)
    movi_code = data['movi_code']
    movi_name = data['movi_name']
    movi_vd = data['movi_vd']
    await state.clear()
    await add_movie(movi_code, movi_name, movi_vd)
    await msg.answer("Kino qo'shildi!", reply_markup=menu_admin)

#  ---------------------------------- ID -----------------------------------
@router_admin.message(Command("id"))
async def id(msg: Message):
    await msg.answer(f"ID: {msg.from_user.id}")

# ----------------------------------- Broadcast --------------------------------
@router_admin.message(Command("broadcast"))
async def broadcast(msg: Message, state: FSMContext):
    await msg.answer("Xabar turini tanlang: \n1. Matn \n2. Rasm \n3. Video \n4. Audio \n5. Hujjat")
    await state.set_state(BroadcastStates.waiting_for_broadcast_type)

@router_admin.message(StateFilter(BroadcastStates.waiting_for_broadcast_type))
async def choose_broadcast_type(msg: Message, state: FSMContext):
    broadcast_type = msg.text
    if broadcast_type in ['1', '2', '3', '4', '5']:
        await state.update_data(broadcast_type=broadcast_type)
        if broadcast_type in ['1', '2', '3', '4', '5']:
            await msg.answer("Xabar matnini yuboring:")
            await state.set_state(BroadcastStates.waiting_for_message)
    else:
        await msg.answer("Iltimos, 1-5 oralig'ida tanlov kiriting.")

@router_admin.message(StateFilter(BroadcastStates.waiting_for_message))
async def receive_message_content(msg: Message, state: FSMContext):
    data = await state.get_data()
    broadcast_type = data.get('broadcast_type')

    # Matn, rasm, video, audio, hujjat uchun caption'ni olish
    if broadcast_type == '1':
        # Matn xabar
        await state.update_data(message_text=msg.text)
        await msg.answer("Xabar uchun caption yuboring (ixtiyoriy):")
        await state.set_state(BroadcastStates.waiting_for_caption)
    elif broadcast_type == '2':
        # Rasm
        await state.update_data(photo_id=msg.photo[-1].file_id)
        await msg.answer("Xabar uchun caption yuboring (ixtiyoriy):")
        await state.set_state(BroadcastStates.waiting_for_caption)
    elif broadcast_type == '3':
        # Video
        await state.update_data(video_id=msg.video.file_id)
        await msg.answer("Xabar uchun caption yuboring (ixtiyoriy):")
        await state.set_state(BroadcastStates.waiting_for_caption)
    elif broadcast_type == '4':
        # Audio
        await state.update_data(audio_id=msg.audio.file_id)
        await msg.answer("Xabar uchun caption yuboring (ixtiyoriy):")
        await state.set_state(BroadcastStates.waiting_for_caption)
    elif broadcast_type == '5':
        # Hujjat
        await state.update_data(document_id=msg.document.file_id)
        await msg.answer("Xabar uchun caption yuboring (ixtiyoriy):")
        await state.set_state(BroadcastStates.waiting_for_caption)

@router_admin.message(StateFilter(BroadcastStates.waiting_for_caption))
async def send_broadcast_message(msg: Message, state: FSMContext):
    data = await state.get_data()
    broadcast_type = data.get('broadcast_type')
    caption = msg.text

    users = await select_users()  # Barcha userlarni olish
    user_ids = [user[1] for user in users]  # User IDlarini olish

    if broadcast_type == '1':
        text = data.get('message_text')
        for user_id in user_ids:
            try:
                await bot.send_message(user_id, text, caption=caption)
            except Exception as e:
                print(f"User {user_id} ga xabar yuborishda xatolik: {e}")
        await msg.answer("Matn xabari yuborildi.")
    elif broadcast_type == '2':
        photo_id = data.get('photo_id')
        for user_id in user_ids:
            try:
                await bot.send_photo(user_id, photo_id, caption=caption)
            except Exception as e:
                print(f"User {user_id} ga rasm yuborishda xatolik: {e}")
        await msg.answer("Rasm yuborildi.")
    elif broadcast_type == '3':
        video_id = data.get('video_id')
        for user_id in user_ids:
            try:
                await bot.send_video(user_id, video_id, caption=caption)
            except Exception as e:
                print(f"User {user_id} ga video yuborishda xatolik: {e}")
        await msg.answer("Video yuborildi.")
    elif broadcast_type == '4':
        audio_id = data.get('audio_id')
        for user_id in user_ids:
            try:
                await bot.send_audio(user_id, audio_id, caption=caption)
            except Exception as e:
                print(f"User {user_id} ga audio yuborishda xatolik: {e}")
        await msg.answer("Audio yuborildi.")
    elif broadcast_type == '5':
        document_id = data.get('document_id')
        for user_id in user_ids:
            try:
                await bot.send_document(user_id, document_id, caption=caption)
            except Exception as e:
                print(f"User {user_id} ga hujjat yuborishda xatolik: {e}")
        await msg.answer("Hujjat yuborildi.")
    
    await state.clear()
