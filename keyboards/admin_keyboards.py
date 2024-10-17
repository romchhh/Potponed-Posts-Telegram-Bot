from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta

def get_admin_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.row(KeyboardButton("Адмін панель 💻"))
    keyboard.row(KeyboardButton("Створити пост"), KeyboardButton("Редагувати пост"))
    keyboard.row(KeyboardButton("Контент план"), KeyboardButton("Налаштування"))
    keyboard.row(KeyboardButton("Шаблони"))
    
    return keyboard



def admin_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton(text="Додати адміністратора", callback_data="admin_add"),
    ]
    keyboard.add(*buttons)
    return keyboard