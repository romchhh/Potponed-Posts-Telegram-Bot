from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext, Dispatcher
from main import bot, dp
from states.admin_states import AdminState
from aiogram.dispatcher import FSMContext
from keyboards.user_keyboards import *
from data.texts import *
from database.user_db import *
from database.admin_db import *
import asyncio, re, os, logging
from keyboards.admin_keyboards import admin_keyboard
import locale
from functions.user_functions import *

# locale.setlocale(locale.LC_TIME, 'uk_UA.UTF-8')  
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dp.callback_query_handler(lambda c: c.data == 'admin_add')
async def add_admin(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    channels = get_user_channels(user_id)
    if not channels:
        add_channel_button = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("➕ Додати канал", callback_data="add_channel")
        )
        await callback_query.message.edit_text(no_channel_text, reply_markup=add_channel_button)
    else:
        channel_buttons = InlineKeyboardMarkup(row_width=2)
        for channel_id, channel_name in channels:
            channel_buttons.add(InlineKeyboardButton(channel_name, callback_data=f"addadmin_{channel_id}"))
        channel_buttons.add(InlineKeyboardButton("➕ Додати канал", callback_data="add_channel"))
        channel_buttons.add(InlineKeyboardButton("← Назад", callback_data="adminback"))
        
        await callback_query.message.edit_text("<b>ДОДАВАННЯ АДМІНІСТРАТОРА:</b>\n\nВиберіть канал, в якому хочете додати адміністратора.", parse_mode='HTML', reply_markup=channel_buttons)

    
    

@dp.callback_query_handler(lambda c: c.data.startswith("addadmin_"))
async def prompt_for_admin_username(callback_query: types.CallbackQuery, state: FSMContext):
    channel_id = callback_query.data.split("_")[1]  # Отримуємо ID каналу з колбеку
    await state.update_data(channel_id=channel_id)  # Зберігаємо ID каналу в стан

    # Кнопка "Назад"
    cancel_button = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("← Назад", callback_data="cancel_add_admin")
    )
    
    # Просимо користувача надіслати username або переслати повідомлення
    await callback_query.message.edit_text(
        "<b>ДОДАВАННЯ АДМІНІСТРАТОРА:</b>\n\nНадішліть username або перешліть повідомлення від користувача, якого хочете зробити адміном.", 
        parse_mode='HTML',
        reply_markup=cancel_button
    )
    
    await AdminState.waiting_for_admin_username.set()

@dp.message_handler(state=AdminState.waiting_for_admin_username, content_types=types.ContentTypes.TEXT)
async def process_admin_username(message: types.Message, state: FSMContext):
    if message.forward_from:
        user_id = message.forward_from.id
        username = message.forward_from.username
        
        user_data = await state.get_data()
        channel_id = user_data['channel_id']
    else:
        username = message.text.strip()
        user_id = get_user_id_by_name(username)  
        if user_id is None:
            await message.answer(f"Користувача з username @{username} не знайдено в базі даних. Перевірте правильність введеного username.")
            await state.finish()
            return  # Повертаємось, не продов
        user_data = await state.get_data()
        channel_id = user_data['channel_id']
    
    # Зберігаємо інформацію у стан перед підтвердженням
    await state.update_data(user_id=user_id, username=username)

    # Інлайн-кнопки "Підтвердити" та "Скасувати"
    confirmation_buttons = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("✓ Підтвердити", callback_data="confirm_add_admin"),
        InlineKeyboardButton("← Скасувати", callback_data="cancel_add_admin")
    )
    
    channel_name = get_channel_name_by_id(channel_id)
    await message.answer(
        f"Ви впевнені, що хочете зробити @{username} адміністратором каналу <b>{channel_name}</b>?",
        reply_markup=confirmation_buttons
    )

@dp.callback_query_handler(lambda c: c.data == "confirm_add_admin", state=AdminState.waiting_for_admin_username)
async def confirm_add_admin(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    user_id = user_data['user_id']
    username = user_data['username']
    channel_id = user_data['channel_id']

    channel_name = get_channel_name_by_id(channel_id)  # функція для отримання назви каналу
    link = get_channel_link_by_id(channel_id)  # функція для отримання посилання на канал, якщо є

    add_admin_to_channel(channel_id, channel_name, user_id, link)

    await callback_query.message.edit_text(
        f"Користувача @{username} додано як адміністратора в канал <b>{channel_name}</b>.", parse_mode="HTML"
    )
    await state.finish()
    
    await bot.send_message(user_id, f"Вас додано як адміністратора в канал <b>{channel_name}</b>.", parse_mode="HTML")
@dp.callback_query_handler(lambda c: c.data == "cancel_add_admin", state=AdminState.waiting_for_admin_username)
async def cancel_add_admin(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()

    await callback_query.answer("Додавання адміністратора скасовано.", show_alert=True)
    keyboard = admin_keyboard()
    await callback_query.message.edit_text("Адмін-панель 👨🏼‍💻", reply_markup=keyboard)  


@dp.callback_query_handler(lambda c: c.data == "cancel_add_admin", state=AdminState.waiting_for_admin_username)
async def cancel_add_admin(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    keyboard = admin_keyboard()
    await callback_query.message.edit_text("Адмін-панель 👨🏼‍💻", reply_markup=keyboard)  
    
    
@dp.callback_query_handler(lambda c: c.data == 'adminback')
async def add_admin(callback_query: types.CallbackQuery): 
    keyboard = admin_keyboard()
    await callback_query.message.edit_text("Адмін-панель 👨🏼‍💻", reply_markup=keyboard)  
    
def register_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(add_admin, lambda c: c.data == 'add_channel')


