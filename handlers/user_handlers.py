from main import bot, dp, Dispatcher, scheduler
from filters.filters import *
from aiogram import types

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputFile

from database.user_db import *
from functions.user_functions import send_mailing
from keyboards.user_keyboards import get_start_keyboard, back_keyboard, generate_calendar
from keyboards.admin_keyboards import get_admin_keyboard, admin_keyboard
from data.texts import *
from states.user_states import EditPostState
import pytz

html = 'HTML'
tz_kiev = pytz.timezone('Europe/Kyiv')
current_time_kiev = datetime.now(tz_kiev).strftime("%H:%M")


async def scheduler_jobs():
    scheduler.add_job(send_mailing, "cron", minute=0) 
    scheduler.add_job(send_mailing, "cron", minute=15) 
    scheduler.add_job(send_mailing, "cron", minute=30) 
    scheduler.add_job(send_mailing, "cron", minute=45) 
    
async def antiflood(*args, **kwargs):
    m = args[0]
    await m.answer("Не спеши :)")

async def on_startup(dp):
    await scheduler_jobs()
    from handlers.user_handlers import dp as user_dp
    from callbacks.user_callbacks.user_callbacks import register_callbacks
    from callbacks.user_callbacks.shedule_callbacks import register_callbacks
    from callbacks.user_callbacks.change_post_callbacks import register_callbacks
    from callbacks.user_callbacks.create_post_callbacks import register_callbacks
    from callbacks.user_callbacks.templates_callbacks import register_callbacks
    from callbacks.admin_callbacks.admin_callbacks import register_callbacks
    register_callbacks(dp)
    me = await bot.get_me()
    # await bot.send_message(logs, f"Бот @{me.username} запущений!")
    print(f"Бот @{me.username} запущений!")

async def on_shutdown(dp):
    me = await bot.get_me()
    # await bot.send_message(logs, f'Bot: @{me.username} зупинений!')
    print(f"Bot: @{me.username} зупинений!")
    
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    
    if user_id in administrators:
        keyboard = get_admin_keyboard()
    else:
        keyboard = get_start_keyboard()

    photo_path = 'data/hello.png'

    await message.answer_photo(
        photo=InputFile(photo_path), 
        caption=welcome_text, 
        parse_mode='HTML', 
        reply_markup=keyboard
    )

    add_user(user_id, user_name)

@dp.message_handler(lambda message: message.text == "Створити пост")
async def create_post(message: types.Message):
    user_id = message.from_user.id
    channels = get_user_channels(user_id)

    if not channels:
        add_channel_button = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("➕ Додати канал", callback_data="add_channel")
        )
        await message.answer(no_channel_text, reply_markup=add_channel_button)
    else:
        channel_buttons = InlineKeyboardMarkup(row_width=2)
        for channel_id, channel_name in channels:
            channel_buttons.add(InlineKeyboardButton(channel_name, callback_data=f"create_post_{channel_id}"))
        channel_buttons.add(InlineKeyboardButton("➕ Додати канал", callback_data="add_channel"))
        
        await message.answer("<b>СТВОРЕННЯ ПОСТУ:</b>\n\nВиберіть канал, в якому хочете створити публікацію.", parse_mode='HTML', reply_markup=channel_buttons)


@dp.message_handler(lambda message: message.text == "Редагувати пост")
async def create_post(message: types.Message):
    user_id = message.from_user.id
    channels = get_user_channels(user_id)

    if not channels:
        add_channel_button = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("➕ Додати канал", callback_data="add_channel")
        )
        await message.answer(no_channel_text, reply_markup=add_channel_button)
    else:
        await message.answer(
            "<b>РЕДАГУВАННЯ ПОСТУ:</b>\n\nПерешліть пост з вашого каналу, який ви хочете відредагувати.",
            parse_mode='HTML',
            reply_markup=back_keyboard()
        )
        # Встановлюємо стан, щоб чекати на пересланий пост
        await EditPostState.waiting_for_post.set()


@dp.message_handler(lambda message: message.text == "Контент план")
async def content_plan(message: types.Message):
    user_id = message.from_user.id
    channels = get_user_channels(user_id)

    if not channels:
        add_channel_button = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("➕ Додати канал", callback_data="add_channel")
        )
        await message.answer(no_channel_text, reply_markup=add_channel_button)
    else:
        current_date = datetime.today()
        scheduled_dates = get_scheduled_times(user_id)  # Fetch scheduled dates from the database
        calendar_buttons = generate_calendar(current_date, scheduled_dates)  # Pass scheduled dates

        await message.answer("<b>КОНТЕНТ ПЛАН:</b>\n\nВ цьому розділі ви можете переглядати и редагувати заплановані пости.", parse_mode='HTML', reply_markup=calendar_buttons)

@dp.message_handler(lambda message: message.text == "Шаблони")
async def templates(message: types.Message):
    user_id = message.from_user.id
    channels = get_user_channels(user_id)
    if not channels:
        add_channel_button = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("➕ Додати канал", callback_data="add_channel")
        )
        await message.answer(no_channel_text, reply_markup=add_channel_button)
    else:
        channel_buttons = InlineKeyboardMarkup(row_width=2)
        for channel_id, channel_name in channels:
            channel_buttons.add(InlineKeyboardButton(channel_name, callback_data=f"create_template_{channel_id}"))
        channel_buttons.add(InlineKeyboardButton("Загальні", callback_data="general_templates"))
        
        await message.answer("<b>ШАБЛОНИ:</b>\n\nЗберігайте шаблони для постів та рекламних креативів.\n\nВиберіть для якого каналу ви хочете переглянути шаблони", parse_mode='HTML', reply_markup=channel_buttons)



@dp.message_handler(lambda message: message.text == "Налаштування")
async def settings(message: types.Message):
    user_id = message.from_user.id
    channels = get_user_channels(user_id)
    if not channels:
        add_channel_button = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("➕ Додати канал", callback_data="add_channel")
        )
        await message.answer(no_channel_text, reply_markup=add_channel_button)
    else:
        channel_buttons = InlineKeyboardMarkup(row_width=2)
        for channel_id, channel_name in channels:
            channel_buttons.add(InlineKeyboardButton(channel_name, callback_data=f"create_post_{channel_id}"))
        channel_buttons.add(InlineKeyboardButton("➕ Додати канал", callback_data="add_channel"))
        channel_buttons.add(InlineKeyboardButton(f"Часовий пояс Київ (UTC+3): {current_time_kiev}", callback_data="timezone_kiev"))
        
        await message.answer("<b>НАЛАШТУВАННЯ:</b>\n\nВ цьому розділі ви можете переглянути налаштування а також додати новий канал в @PostponedPosterBot.", parse_mode='HTML', reply_markup=channel_buttons)


@dp.message_handler(lambda message: message.text == "Адмін панель 💻")
@dp.throttled(antiflood, rate=1)
async def admin_panel(message: types.Message):
    user_id = message.from_user.id
    if user_id in administrators:
        keyboard = admin_keyboard()
        await message.answer("Адмін панель 💻", reply_markup=keyboard)