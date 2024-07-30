from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu_admin = ReplyKeyboardMarkup(
    resize_keyboard=True, 
    keyboard=[
        [KeyboardButton(text='Barcha kinolar'), KeyboardButton(text='Yangi kino qo\'shish')]
    ]
)