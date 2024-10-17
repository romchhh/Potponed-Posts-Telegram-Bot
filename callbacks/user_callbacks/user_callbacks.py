from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext, Dispatcher
from main import bot, dp
from states.user_states import AddChannelState, Form, EditPostState, Template
from aiogram.dispatcher import FSMContext
from keyboards.user_keyboards import *
from database.user_db import add_channel_to_db
from data.texts import *
from database.user_db import *
import asyncio, re, os, logging
import locale
from functions.user_functions import *

# locale.setlocale(locale.LC_TIME, 'uk_UA.UTF-8')  
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

    
    
@dp.callback_query_handler(lambda c: c.data == 'add_channel')
async def prompt_for_channel(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(
        add_channel_text, reply_markup=get_back_keyboard()
    )
    await AddChannelState.waiting_for_channel.set()
    

    
@dp.message_handler(state=AddChannelState.waiting_for_channel, content_types=types.ContentType.ANY)
async def process_channel_info(message: types.Message, state: FSMContext):
    channel = None
    channel_id = None
    channel_title = None

    if message.text and message.text.startswith("https://t.me/"):
        try:
            # Вилучаємо юзернейм або ID каналу з посилання
            channel_username = message.text.split("/")[-1].strip()
            print(f"Отримано посилання на канал: {message.text}, юзернейм: {channel_username}")
            
            # Отримуємо інформацію про канал за юзернеймом
            channel = await bot.get_chat(message.text)
            channel_id = channel.id
            channel_title = channel.title
            print(f"Інформація про канал: ID - {channel_id}, Назва - {channel_title}")
        except Exception as e:
            print(f"Помилка отримання інформації про канал: {e}")
            await message.answer("Не вдалося отримати інформацію про канал. Перевірте посилання та спробуйте ще раз або просто перешлыть будь яке повідомлення з каналу.")
            await state.finish()
            return
    elif message.forward_from_chat:
        channel = message.forward_from_chat
        channel_id = channel.id
        channel_title = channel.title
        print(f"Отримано переслане повідомлення з каналу: ID - {channel_id}, Назва - {channel_title}")
    else:
        await message.answer("Перешліть правильне повідомлення з каналу або надішліть посилання.")
        return

    try:
        # Отримуємо додаткову інформацію про канал (наприклад, посилання на запрошення)
        channel_info = await bot.get_chat(channel_id)
        link = channel_info.invite_link or f"https://t.me/{channel_info.username}"  # Використовуємо юзернейм, якщо немає invite_link
        print(f"Інформація про канал: {channel_info}")
    except Exception as e:
        print(f"Помилка отримання детальної інформації про канал: {e}")
        await message.answer("Не вдалося отримати інформацію про канал.")
        await state.finish()
        return

    try:
        # Перевіряємо чи є бот адміністратором на каналі
        member = await bot.get_chat_member(channel_id, (await bot.me).id)
        print(f"Статус бота в каналі: {member.status}")
        if member.status not in ['administrator', 'creator']:
            await message.answer("Бот повинен бути адміністратором на цьому каналі для додавання.")
            await state.finish()
            return
    except Exception as e:
        print(f"Помилка перевірки прав бота на каналі: {e}")
        await message.answer("Не вдалося перевірити права бота на цьому каналі.")
        await state.finish()
        return

    try:
        # Перевіряємо чи є користувач адміністратором на каналі
        user_member = await bot.get_chat_member(channel_id, message.from_user.id)
        print(f"Статус користувача в каналі: {user_member.status}")
        if user_member.status not in ['administrator', 'creator']:
            await message.answer("Ви повинні бути адміністратором або власником цього каналу для додавання.")
            await state.finish()
            return
    except Exception as e:
        print(f"Помилка перевірки прав користувача на каналі: {e}")
        await message.answer("Не вдалося перевірити права користувача на цьому каналі.")
        await state.finish()
        return

    try:
        # Додаємо канал до бази даних
        if add_channel_to_db(channel_id, channel_title, message.from_user.id, link):
            print(f"Канал успішно додано до бази: ID - {channel_id}, Назва - {channel_title}")
            await message.answer(
                f"Ви успішно підключили канал <a href='{link}'>{channel_title}</a> до <b>PosterBot</b>!",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("Повернутися до меню", callback_data="back_to_menu")
                )
            )
        else:
            print(f"Канал вже підключений раніше: {channel_title}")
            await message.answer(f"Канал {channel_title} вже був підключений раніше!")
    except Exception as e:
        print(f"Помилка при додаванні каналу до бази даних: {e}")
        await message.answer("Помилка при додаванні каналу до бази даних.")

    await state.finish()




 
@dp.callback_query_handler(text="back_to_posts", state=(AddChannelState.waiting_for_channel, Form.content))
async def process_channel_info(callback_query: types.CallbackQuery, state: FSMContext):
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
            channel_buttons.add(InlineKeyboardButton(channel_name, callback_data=f"create_post_{channel_id}"))
        channel_buttons.add(InlineKeyboardButton("➕ Додати канал", callback_data="add_channel"))
        
        await callback_query.message.edit_text("<b>СТВОРЕННЯ ПОСТУ:</b>\n\nВиберіть канал, в якому хочете створити публікацію.", parse_mode='HTML', reply_markup=channel_buttons)

    await callback_query.answer()
    await state.finish()


@dp.callback_query_handler(text="back_to_menu")
async def process_channel_info(callback_query: types.CallbackQuery):
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
            channel_buttons.add(InlineKeyboardButton(channel_name, callback_data=f"create_post_{channel_id}"))
        channel_buttons.add(InlineKeyboardButton("➕ Додати канал", callback_data="add_channel"))
        
        await callback_query.message.edit_text("<b>СТВОРЕННЯ ПОСТУ:</b>\n\nВиберіть канал, в якому хочете створити публікацію.", parse_mode='HTML', reply_markup=channel_buttons)

    await callback_query.answer()
    
    
@dp.callback_query_handler(text="back_to")
async def process_channel_info(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    
@dp.callback_query_handler(text="back_to_my_post", state=(Form.content, Form.media, Form.description, Form.url_buttons, EditPostState.waiting_for_post, EditPostState.waiting_for_new_buttons, EditPostState.waiting_for_new_text, Template.content, Template.url_buttons, Template.description, Template.media))
async def process_channel_info(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await state.finish()




def register_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(prompt_for_channel, lambda c: c.data == 'add_channel')