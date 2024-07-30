from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command, Filter
from aiogram import F
from loader import bot, router_admin, db_movies, db_user
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.defoult.defoult_key import *
from keyboards.inline.inline_key import *

class Movies(StatesGroup):
    movi_code = State()
    movi_name = State()
    movi_vd = State()

class Admin(Filter):
    def __init__(self, admin_id: int):
        self.admin_id = admin_id

    async def __call__(self, msg: Message):
        return msg.from_user.id == self.admin_id

ADMIN_ID = "ADMIN_ID"

# ----------------------------------- START --------------------------------
@router_admin.message(CommandStart(), Admin(ADMIN_ID))
async def start(msg: Message):
    await msg.answer("Assalomu aleykum Admin!\n\nBuyruqlar:\nid - ID olish", reply_markup=menu_admin)

# ----------------------------------- All movies --------------------------------
@router_admin.message(F.text == 'Barcha kinolar')
async def all_movies(msg: Message):
    movies = db_movies.select_movies()
    movies_str = "\n".join([f"Kino IDsi: <b>{movie[0]}</b>, Kino kodi va nomi: <b>{movie[1]} - {movie[2]}</b>" for movie in movies])
    await msg.answer(movies_str, reply_markup=menu_admin)

# ----------------------------------- ADD movies --------------------------------

@router_admin.message(F.text == 'Yangi kino qo\'shish')
async def add_movi_code(msg: Message, state: FSMContext):
    db_movies.create_table()
    await state.set_state(Movies.movi_code)
    await msg.answer("Kino kodini yuboring!")

@router_admin.message(Movies.movi_code)
async def movi_code_set(msg: Message, state: FSMContext):
    await state.update_data(movi_code=msg.text)
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
    db_movies.add_movies(movi_code, movi_name, movi_vd)
    await msg.answer("Kino qo'shildi!", reply_markup=menu_admin)

#  ---------------------------------- ID -----------------------------------
@router_admin.message(Command("id"))
async def id(msg: Message):
    await msg.answer(f"ID: {msg.from_user.id}")