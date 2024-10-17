from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext, Dispatcher
from main import bot, dp
from states.user_states import Form
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from keyboards.user_keyboards import *
from data.texts import *
from database.user_db import *
import asyncio, re, os
from aiogram.utils.exceptions import TelegramAPIError
from datetime import datetime, timedelta
from functions.user_functions import *


user_data = {}

@dp.callback_query_handler(Text(startswith='create_post_'))
async def process_channel_selection(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[-1]
    channel_name = get_channel_name_by_id(channel_id)

    # Зберігаємо канал в глобальний словник та FSMContext
    user_data[user_id] = {'channel_id': channel_id}
    await state.update_data(channel_id=channel_id)

    await Form.content.set()
    await callback_query.message.edit_text(
        f"Будь ласка, надішліть те, що ви хочете опублікувати на каналі <b>{channel_name}</b>:",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Назад", callback_data="back_to_posts")
        )
    )

@dp.message_handler(state=Form.content, content_types=['text', 'photo', 'video', 'document'])
async def handle_content(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    channel_id = data.get('channel_id')

    content_type = message.content_type
    content_info = ""
    media_info = None
    media_type = None
    html_content = None  # Initialize html_content

    if content_type == 'text':
        content_info = message.text
        entities = message.entities 
        print(entities)

        if entities:
            html_content = format_entities(content_info, entities)
            print(html_content)
        else:
            html_content = content_info  # Assign content_info if no entities

        await message.answer(html_content, parse_mode='HTML', reply_markup=create_post(channel_id, user_data, user_id, user_data[user_id].get('url_buttons')))
        media_type = None
    elif content_type == 'photo':
        media_info = message.photo[-1].file_id
        await message.answer_photo(media_info, reply_markup=create_post(channel_id, user_data, user_id, user_data[user_id].get('url_buttons')))
        media_type = 'photo'
    elif content_type == 'video':
        media_info = message.video.file_id
        await message.answer_video(media_info, reply_markup=create_post(channel_id, user_data, user_id, user_data[user_id].get('url_buttons')))
        media_type = 'video'
    elif content_type == 'document':
        media_info = message.document.file_id
        await message.answer_document(media_info, reply_markup=create_post(channel_id, user_data, user_id, user_data[user_id].get('url_buttons')))
        media_type = 'document'
    else:
        await message.answer("Невідомий формат.")

    # Оновлюємо глобальний словник і стан
    if html_content:
        user_data[user_id]['content'] = html_content
        await state.update_data(content=html_content)

    user_data[user_id]['media'] = media_info
    user_data[user_id]['media_type'] = media_type

    await state.finish()

    
@dp.callback_query_handler(Text(startswith='media_'))
async def handle_media(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[-1]

    # Оновлюємо дані в глобальному словнику
    user_data[user_id]['channel_id'] = channel_id

    await Form.media.set()
    await callback_query.message.answer(
        "Будь ласка, надішліть медіа, яке ви хочете додати або змінити:",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Назад", callback_data="back_to_my_post")
        )
    )

@dp.message_handler(state=Form.media, content_types=['photo', 'video', 'document'])
async def handle_media_content(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channel_id = user_data[user_id]['channel_id']

    media_info = None
    media_type = None
    if message.content_type == 'photo':
        media_info = message.photo[-1].file_id
        media_type = 'photo'
    elif message.content_type == 'video':
        media_info = message.video.file_id
        media_type = 'video'
    elif message.content_type == 'document':
        media_info = message.document.file_id
        media_type = 'document'

    # Оновлюємо глобальний словник
    user_data[user_id]['media'] = media_info
    user_data[user_id]['media_type'] = media_type

    content_info = user_data[user_id].get('content')

    if media_info:
        if media_type == 'photo':
            await message.answer_photo(media_info, caption=f"{content_info}", parse_mode='HTML', reply_markup=create_post(channel_id, user_data, user_id, user_data[user_id].get('url_buttons')))
        elif media_type == 'video':
            await message.answer_video(media_info, caption=f"{content_info}", parse_mode='HTML', reply_markup=create_post(channel_id, user_data, user_id, user_data[user_id].get('url_buttons')))
        elif media_type == 'document':
            await message.answer_document(media_info, caption=f"{content_info}", parse_mode='HTML', reply_markup=create_post(channel_id, user_data, user_id, user_data[user_id].get('url_buttons')))
    else:
        await message.answer(f"{content_info}", parse_mode='HTML', reply_markup=create_post(channel_id, user_data, user_id, user_data[user_id].get('url_buttons')))

    await state.finish()

@dp.callback_query_handler(Text(startswith='add_'))
async def handle_description(callback_query: types.CallbackQuery, state: FSMContext):
    await Form.description.set()
    await callback_query.message.answer(
        "Будь ласка, надішліть опис, який ви хочете додати або змінити:",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Назад", callback_data="back_to_my_post")
        )
    )

@dp.message_handler(state=Form.description, content_types=['text'])
async def handle_description_content(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channel_id = user_data[user_id]['channel_id']
    media_info = user_data[user_id].get('media')
    media_type = user_data[user_id].get('media_type')
    
    content_info = message.text
    entities = message.entities 
    formatted_content = format_entities(content_info, entities)
    
    user_data[user_id]['content'] = formatted_content
    print(user_data)

    # Якщо медіа є, надсилаємо медіа з описом
    if media_info:
        # Перевірка типу медіа
        if media_type == 'photo':
            await message.answer_photo(media_info, caption=formatted_content, parse_mode='HTML', reply_markup=create_post(channel_id, user_data, user_id, user_data[user_id].get('url_buttons')))
        elif media_type == 'video':
            await message.answer_video(media_info, caption=formatted_content, parse_mode='HTML', reply_markup=create_post(channel_id, user_data, user_id, user_data[user_id].get('url_buttons')))
        elif media_type == 'document':
            await message.answer_document(media_info, caption=formatted_content, parse_mode='HTML', reply_markup=create_post(channel_id, user_data, user_id, user_data[user_id].get('url_buttons')))
    else:
        # Якщо немає медіа, надсилаємо лише текст
        await message.answer(formatted_content, parse_mode='HTML', reply_markup=create_post(channel_id, user_data, user_id, user_data[user_id].get('url_buttons')))

    await state.finish()


@dp.callback_query_handler(Text(startswith='url_buttons_'))
async def handle_url_buttons(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[-1]

    # Оновлюємо дані в глобальному словнику
    user_data[user_id]['channel_id'] = channel_id

    await Form.url_buttons.set()
    await callback_query.message.answer(
        "<b>URL-КНОПКИ</b>\n\n"
        "Будь ласка, надішліть список URL-кнопок у форматі:\n\n"
        "<code>Кнопка 1 - http://link.com\n"
        "Кнопка 2 - http://link.com</code>\n\n"
        "Використовуйте роздільник <code>' | '</code>, щоб додати до 8 кнопок в один ряд (допустимо 15 рядів):\n\n"
        "<code>Кнопка 1 - http://link.com | Кнопка 2 - http://link.com</code>\n\n",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Назад", callback_data="back_to_my_post")
        ),
        disable_web_page_preview=True  # Додайте цей параметр, щоб вимкнути попередній перегляд
    )


@dp.message_handler(state=Form.url_buttons, content_types=['text'])
async def handle_url_buttons_content(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channel_id = user_data[user_id]['channel_id']
    media_info = user_data[user_id].get('media')
    media_type = user_data[user_id].get('media_type')
    content_info = user_data[user_id].get('content')

    url_buttons_text = message.text
    url_buttons = parse_url_buttons(url_buttons_text)

    # Оновлюємо URL-кнопки в глобальному словнику
    user_data[user_id]['url_buttons'] = url_buttons

    # Якщо медіа є, надсилаємо медіа з описом і URL-кнопками
    if media_info:
        if media_type == 'photo':
            await message.answer_photo(media_info, caption=f"{content_info}", parse_mode='HTML', reply_markup=create_post(channel_id, user_data, user_id, url_buttons))
        elif media_type == 'video':
            await message.answer_video(media_info, caption=f"{content_info}", parse_mode='HTML', reply_markup=create_post(channel_id, user_data, user_id, url_buttons))
        elif media_type == 'document':
            await message.answer_document(media_info, caption=f"{content_info}", parse_mode='HTML', reply_markup=create_post(channel_id, user_data, user_id, url_buttons))
    else:
        # Якщо немає медіа, надсилаємо лише текст з URL-кнопками
        await message.answer(f"{content_info}", parse_mode='HTML', reply_markup=create_post(channel_id, user_data, user_id, url_buttons))

    await state.finish()


    
@dp.callback_query_handler(Text(startswith='comments_'))
async def handle_comments(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = user_data[user_id]['channel_id']
    if 'comments' not in user_data[user_id]:
        user_data[user_id]['comments'] = 0  # 0 - коментарі вимкнені
    user_data[user_id]['comments'] = 1 if user_data[user_id]['comments'] == 0 else 0
    await callback_query.message.edit_reply_markup(reply_markup=create_post(channel_id, user_data, user_id, user_data[user_id].get('url_buttons')))


@dp.callback_query_handler(Text(startswith='pin_'))
async def handle_comments(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = user_data[user_id]['channel_id']
    if 'pin' not in user_data[user_id]:
        user_data[user_id]['pin'] = 0 
    user_data[user_id]['pin'] = 1 if user_data[user_id]['pin'] == 0 else 0
    await callback_query.message.edit_reply_markup(reply_markup=create_post(channel_id, user_data, user_id, user_data[user_id].get('url_buttons')))


@dp.callback_query_handler(Text(startswith='bell_'))
async def handle_comments(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = user_data[user_id]['channel_id']
    if 'bell' not in user_data[user_id]:
        user_data[user_id]['bell'] = 0  # 0 - коментарі вимкнені
    user_data[user_id]['bell'] = 1 if user_data[user_id]['bell'] == 0 else 0
    await callback_query.message.edit_reply_markup(reply_markup=create_post(channel_id, user_data, user_id, user_data[user_id].get('url_buttons')))
    
@dp.callback_query_handler(Text(startswith='addpost_'))
async def handle_comments(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = user_data[user_id]['channel_id']
    if 'addpost' not in user_data[user_id]:
        user_data[user_id]['addpost'] = 0  # 0 - коментарі вимкнені
    user_data[user_id]['addpost'] = 1 if user_data[user_id]['addpost'] == 0 else 0
    await callback_query.message.edit_reply_markup(reply_markup=publish_post(channel_id, user_data, user_id))

    
@dp.callback_query_handler(Text(startswith='next_'))
async def handle_url_buttons(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[-1]
    channel_name = get_channel_name_by_id(channel_id)
    
    await callback_query.message.answer("<b>💼 НАЛАШТУВАННЯ ВІДПРАВКИ</b>\n\n"
                                           f"Пост готовий до публикації на каналі {channel_name}.", parse_mode='HTML', reply_markup=publish_post(channel_id, user_data, user_id))
    
    
@dp.callback_query_handler(Text(startswith='timer_back'), state=Form.schedule_post)
async def handle_url_buttons(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[-1]
    channel_name = get_channel_name_by_id(channel_id)
    await state.finish()
    
    await callback_query.message.edit_text("<b>💼 НАЛАШТУВАННЯ ВІДПРАВКИ</b>\n\n"
                                           f"Пост готовий до публикації на каналі {channel_name}.", parse_mode='HTML', reply_markup=publish_post(channel_id, user_data, user_id))
    
  
    
    
@dp.callback_query_handler(Text(startswith='publish_'))
async def confirm_publish(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[1] 
    confirm_keyboard = InlineKeyboardMarkup(row_width=2)
    confirm_keyboard.add(
        InlineKeyboardButton("✓ Так", callback_data=f"confirm_publish_{channel_id}"),
        InlineKeyboardButton("❌ Ні", callback_data="cancel_publish")
    )

    await callback_query.message.edit_text("Ви впевнені, що хочете опублікувати пост?", reply_markup=confirm_keyboard)

@dp.callback_query_handler(Text(startswith='confirm_publish_'))
async def handle_publish_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[-1]  # Get channel_id
    print(channel_id)

    media_info = user_data[user_id].get('media')
    media_type = user_data[user_id].get('media_type')
    content_info = user_data[user_id].get('content')
    url_buttons = user_data[user_id].get('url_buttons')

    bell = user_data[user_id].get('bell', 0)  # Default to 0 if not set
    disable_notification = (bell == 0)  # Disable notification if bell == 0
    pin_message = user_data[user_id].get('pin', 0) == 1  # True if pin == 1
    if media_info:
        if media_type == 'photo':
            message = await bot.send_photo(channel_id, media_info, caption=content_info, parse_mode='HTML', reply_markup=post_keyboard(channel_id, user_data, user_id, url_buttons), disable_notification=disable_notification, )
        elif media_type == 'video':
            message = await bot.send_video(channel_id, media_info, caption=content_info, parse_mode='HTML', reply_markup=post_keyboard(channel_id, user_data, user_id, url_buttons), disable_notification=disable_notification)
        elif media_type == 'document':
            message = await bot.send_document(channel_id, media_info, caption=content_info, parse_mode='HTML', reply_markup=post_keyboard(channel_id, user_data, user_id, url_buttons), disable_notification=disable_notification)
    else:
        message = await bot.send_message(channel_id, content_info, parse_mode='HTML', reply_markup=post_keyboard(channel_id, user_data, user_id, url_buttons), disable_notification=disable_notification)
    if pin_message:
        await bot.pin_chat_message(channel_id, message.message_id)

    await callback_query.answer("Пост опубліковано!", show_alert=True)
    await asyncio.sleep(2) 
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


@dp.callback_query_handler(Text(equals='cancel_publish'))
async def cancel_publish(callback_query: types.CallbackQuery):
    await callback_query.answer("Публікацію скасовано.", show_alert=True)
    await asyncio.sleep(2) 
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


@dp.callback_query_handler(Text(startswith='timer_'))
async def handle_timer(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[-1]
    
    back_keyboard = InlineKeyboardMarkup(row_width=2)
    back_keyboard.add(InlineKeyboardButton("← Назад", callback_data=f"timer_back{channel_id}"))

    await Form.schedule_post.set()  # Set the new state
    await callback_query.message.edit_text(
        "<b>🕔 ВІДКЛАДЕНИЙ ПОСТ</b>\n\n"
        "Відправте час публікування вашого поста (GMT+2 Київ) в форматі (DD.MM.YYYY HH:MM), наприклад:\n\n"
        "<code>02.10.2024 12:00\n"
        "23.05.2025 05:30</code>", 
        parse_mode='HTML', reply_markup=back_keyboard
    )

@dp.message_handler(state=Form.schedule_post)
async def process_schedule_post(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channel_id = user_data[user_id].get('channel_id')  # Get the channel ID from user_data
    channel_name = get_channel_name_by_id(channel_id)

    # Regex to validate the date format DD.MM.YYYY HH:MM
    date_pattern = r'^\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}$'
    
    if re.match(date_pattern, message.text):
        try:
            scheduled_time = datetime.datetime.strptime(message.text, "%d.%m.%Y %H:%M")
            
            if scheduled_time < datetime.datetime.now():
                await message.answer("Вибачте, але ви не можете запланувати пост у минулому. Спробуйте ще раз.")
                return  # Exit the function and wait for new input
            
            confirmation_text = (
                f"Запланувати пост в канал <b>{channel_name}</b> "
                f"на {scheduled_time.strftime('%A, %d %B %Y')} "
                f"в {scheduled_time.strftime('%H:%M')}?"
            )

            confirm_keyboard = InlineKeyboardMarkup(row_width=1)
            confirm_keyboard.add(
                InlineKeyboardButton("✓ Так, запланувати", callback_data=f"confirm_schedule_{channel_id}_{scheduled_time.timestamp()}"),
                InlineKeyboardButton("← Назад", callback_data=f"next_{channel_id}")
            )

            await message.answer(confirmation_text, parse_mode='HTML', reply_markup=confirm_keyboard)
            await state.finish()  # Clear the state after confirmation message
        except ValueError:
            await message.answer("Неправильний формат дати. Спробуйте ще раз.")
    else:
        await message.answer("Неправильний формат. Використовуйте (DD.MM.YYYY HH:MM).")
    
     
@dp.callback_query_handler(Text(startswith='confirm_schedule_'))
async def handle_schedule_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    data = callback_query.data.split('_')
    channel_id = data[2]
    scheduled_time = datetime.datetime.fromtimestamp(float(data[3]))

    media_info = user_data[user_id].get('media')
    media_type = user_data[user_id].get('media_type')
    content_info = user_data[user_id].get('content')
    url_buttons = user_data[user_id].get('url_buttons')
    bell = user_data[user_id].get('bell', 0)
    pin = user_data[user_id].get('pin', 0)

    media_path = None
    if media_info:
        file = await bot.get_file(media_info)
        original_file_name = file.file_path.split('/')[-1]

        media_dir = f'posts/{user_id}/'
        os.makedirs(media_dir, exist_ok=True)

        media_path = os.path.join(media_dir, original_file_name)

        try:
            await download_media(media_info, media_path)
        except TelegramAPIError as e:
            await callback_query.answer(f"Помилка завантаження медіа: {e}", show_alert=True)
            return
    print(url_buttons)
    url_buttons_str = str(url_buttons) if url_buttons else None
    print(url_buttons_str)
    save_post_to_db(user_id, channel_id, content_info, media_type, media_path, url_buttons_str, bell, pin, scheduled_time)

    await callback_query.answer("Пост заплановано!", show_alert=True)
    await asyncio.sleep(2)
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

def register_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(process_channel_selection, lambda c: c.data == 'add_channel')