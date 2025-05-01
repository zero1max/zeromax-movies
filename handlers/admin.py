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

class AdminStates(StatesGroup):
    waiting_for_password = State()
    waiting_for_new_admin_id = State()


class Admin(Filter):
    def __init__(self, admin_ids: list[int]):
        self.admin_ids = admin_ids

    async def __call__(self, msg: Message):
        return msg.from_user.id in self.admin_ids

ADMIN_PASSWORD = "secret123"
ADMIN_IDS = [5471452269]

# ----------------------------------- START --------------------------------
@router_admin.message(CommandStart(), Admin(ADMIN_IDS))
async def start(msg: Message):
    await msg.answer("Assalomu aleykum Admin!\n\nBuyruqlar:\n/id - ID olish\n/broadcast - Userlarda xabar yuborish\n/get_db - sqlite ni olish", reply_markup=menu_admin)

# ----------------------------------- Sqlite olish --------------------------------
@router_admin.message(Command('get_db'), Admin(ADMIN_IDS))
async def get_db(msg: Message, action=ChatAction.UPLOAD_DOCUMENT):
    db_path = './movies.db'
    database = FSInputFile(db_path)

    await bot.send_document(chat_id=ADMIN_IDS, document=database)

# ----------------------------------- All movies --------------------------------
@router_admin.message(F.text == 'Barcha kinolar', Admin(ADMIN_IDS))
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

@router_admin.message(F.text == 'Yangi kino qo\'shish', Admin(ADMIN_IDS))
async def add_movi_code(msg: Message, state: FSMContext):
    await state.set_state(Movies.movi_code)
    await msg.answer("Kino kodini yuboring!")

@router_admin.message(Movies.movi_code, Admin(ADMIN_IDS))
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

@router_admin.message(Movies.movi_name, Admin(ADMIN_IDS))
async def movi_name_set(msg: Message, state: FSMContext):
    await state.update_data(movi_name=msg.text)
    await state.set_state(Movies.movi_vd)
    await msg.answer("Kino videosini yuboring!")

@router_admin.message(Movies.movi_vd, Admin(ADMIN_IDS))
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
@router_admin.message(Command("broadcast"), Admin(ADMIN_IDS))
async def broadcast(msg: Message, state: FSMContext):
    await msg.answer("Xabar turini tanlang: \n1. Matn \n2. Rasm \n3. Video \n4. Audio \n5. Hujjat")
    await state.set_state(BroadcastStates.waiting_for_broadcast_type)


@router_admin.message(StateFilter(BroadcastStates.waiting_for_broadcast_type), Admin(ADMIN_IDS))
async def choose_broadcast_type(msg: Message, state: FSMContext):
    if msg.text not in ['1', '2', '3', '4', '5']:
        await msg.answer("Iltimos, 1-5 oralig'ida tanlov kiriting.")
        return

    await state.update_data(broadcast_type=msg.text)
    await msg.answer("Xabarni yuboring (fayl yoki matn):")
    await state.set_state(BroadcastStates.waiting_for_message)


@router_admin.message(StateFilter(BroadcastStates.waiting_for_message), Admin(ADMIN_IDS))
async def receive_message_content(msg: Message, state: FSMContext):
    data = await state.get_data()
    b_type = data.get('broadcast_type')

    if b_type == '1' and msg.text:
        await state.update_data(message_text=msg.text)

    elif b_type == '2' and msg.photo:
        await state.update_data(photo_id=msg.photo[-1].file_id)

    elif b_type == '3' and msg.video:
        await state.update_data(video_id=msg.video.file_id)

    elif b_type == '4' and msg.audio:
        await state.update_data(audio_id=msg.audio.file_id)

    elif b_type == '5' and msg.document:
        await state.update_data(document_id=msg.document.file_id)

    else:
        await msg.answer("Noto'g'ri format! Iltimos, mos xabar yuboring.")
        return

    await msg.answer("Xabar uchun caption yuboring (ixtiyoriy, agar caption xohlamasangiz /skip yuboring):")
    await state.set_state(BroadcastStates.waiting_for_caption)


@router_admin.message(StateFilter(BroadcastStates.waiting_for_caption), Admin(ADMIN_IDS))
async def send_broadcast_message(msg: Message, state: FSMContext):
    data = await state.get_data()
    b_type = data.get('broadcast_type')

    # Agar foydalanuvchi '/skip' yuborsa, captionni bo‘sh qoldiramiz
    caption = "" if msg.text == "/skip" else msg.text or ""

    users = await select_users()
    user_ids = [user[1] for user in users]

    sent_count = 0
    for user_id in user_ids:
        try:
            if b_type == '1':
                await bot.send_message(user_id, data.get('message_text'))
            elif b_type == '2':
                await bot.send_photo(user_id, data.get('photo_id'), caption=caption or None)
            elif b_type == '3':
                await bot.send_video(user_id, data.get('video_id'), caption=caption or None)
            elif b_type == '4':
                await bot.send_audio(user_id, data.get('audio_id'), caption=caption or None)
            elif b_type == '5':
                await bot.send_document(user_id, data.get('document_id'), caption=caption or None)
            sent_count += 1
        except Exception as e:
            print(f"Xatolik: foydalanuvchi {user_id}: {e}")

    await msg.answer(f"Xabar {sent_count} foydalanuvchiga yuborildi.")
    await state.clear()

# ---------------------------------------- Add New Admin ------------------------------
@router_admin.message(F.text == "Admin qo'shish", Admin(ADMIN_IDS))
async def request_password(msg: Message, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_password)
    await msg.answer("Iltimos, parolni kiriting:")

@router_admin.message(AdminStates.waiting_for_password, Admin(ADMIN_IDS))
async def check_password(msg: Message, state: FSMContext):
    if msg.text == ADMIN_PASSWORD:
        await state.set_state(AdminStates.waiting_for_new_admin_id)
        await msg.answer("Parol to'g'ri ✅\nIltimos, yangi adminning ID sini kiriting:")
    else:
        await state.clear()
        await msg.answer("❌ Uzr, siz admin qo'shish huquqiga ega emassiz.")

@router_admin.message(AdminStates.waiting_for_new_admin_id, Admin(ADMIN_IDS))
async def add_new_admin(msg: Message, state: FSMContext):
    try:
        new_admin_id = int(msg.text)
    except ValueError:
        await msg.answer("❌ Iltimos, faqat raqamli ID kiriting!")
        return

    if new_admin_id in ADMIN_IDS:
        await msg.answer("Bu ID allaqachon adminlar ro'yxatida.")
    else:
        ADMIN_IDS.append(new_admin_id)
        await msg.answer(f"✅ Admin muvaffaqiyatli qo‘shildi: {new_admin_id}")

    await state.clear()
