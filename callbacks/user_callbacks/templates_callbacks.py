from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.dispatcher import FSMContext, Dispatcher
from main import bot, dp
from states.user_states import Template, PublishTemplate
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from keyboards.user_keyboards import *
from data.texts import *
from database.user_db import *
import asyncio, re, os, ast
from aiogram.utils.exceptions import TelegramAPIError
from datetime import datetime
from functions.user_functions import *

template_data = {}


@dp.callback_query_handler(lambda c: c.data.startswith('create_template_'))
async def handle_create_template(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[2]


    templates = get_templates_for_channel(user_id, channel_id)
    
    no_keyboard = InlineKeyboardMarkup(row_width=1)
    no_keyboard.add(InlineKeyboardButton(text="➕ Додати шаблон", callback_data=f"addtemplate_{channel_id}"))
    no_keyboard.add(InlineKeyboardButton(text="← Назад", callback_data=f"back_to_channels"))
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    for template in templates:
        media_type = template[4]  #
        content = template[3]  

        if media_type == 'photo':
            button_text = f"📷 {content[:10] if content else ''}"
        elif media_type == 'video':
            button_text = f"🎥 {content[:10] if content else ''}"
        else:
            button_text = content[:10] if content else 'Без тексту'

        keyboard.add(InlineKeyboardButton(text=button_text, callback_data=f"template_{template[0]}"))

    
    keyboard.add(InlineKeyboardButton(text="➕ Додати шаблон", callback_data=f"addtemplate_{channel_id}"))
    keyboard.add(InlineKeyboardButton(text="← Назад", callback_data=f"back_to_channels"))

    if not templates:
        await callback_query.message.edit_text("Немає шаблонів для обраного каналу:", reply_markup=no_keyboard)
    else:
        await callback_query.message.edit_text("Оберіть шаблон для редагування або перегляду:", reply_markup=keyboard)



@dp.callback_query_handler(lambda c: c.data.startswith('general_templates'))
async def handle_create_template(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    templates = get_templates_for_channel(user_id, 1)

    no_keyboard = InlineKeyboardMarkup(row_width=1)
    no_keyboard.add(InlineKeyboardButton(text="➕ Додати шаблон", callback_data=f"addtemplate_1"))
    no_keyboard.add(InlineKeyboardButton(text="← Назад", callback_data=f"back_to_channels"))
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    for template in templates:
        media_type = template[4]  #
        content = template[3]  

        if media_type == 'photo':
            button_text = f"📷 {content[:10] if content else ''}"
        elif media_type == 'video':
            button_text = f"🎥 {content[:10] if content else ''}"
        else:
            button_text = content[:10] if content else 'Без тексту'

        keyboard.add(InlineKeyboardButton(text=button_text, callback_data=f"template_{template[0]}"))

    
    keyboard.add(InlineKeyboardButton(text="➕ Додати шаблон", callback_data=f"addtemplate_1"))
    keyboard.add(InlineKeyboardButton(text="← Назад", callback_data=f"back_to_channels"))

    if not templates:
        await callback_query.message.edit_text("Немає загальних шаблонів:", reply_markup=no_keyboard)
    else:
        await callback_query.message.edit_text("Оберіть шаблон для редагування або перегляду:", reply_markup=keyboard)



@dp.callback_query_handler(lambda c: c.data == 'back_to_channels')
async def handle_back_to_channels(callback_query: types.CallbackQuery):
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
            channel_buttons.add(InlineKeyboardButton(channel_name, callback_data=f"create_template_{channel_id}"))
        channel_buttons.add(InlineKeyboardButton("Загальні", callback_data="general_templates"))

        await callback_query.message.edit_text(
            "<b>ШАБЛОНИ:</b>\n\nЗберігайте шаблони для постів та рекламних креативів.\n\nВиберіть для якого каналу ви хочете переглянути шаблони",
            parse_mode='HTML',
            reply_markup=channel_buttons
        )


template_data = {}

@dp.callback_query_handler(Text(startswith='addtemplate_'))
async def process_channel_selection(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[-1]
    channel_name = get_channel_name_by_id(channel_id)

    # Зберігаємо канал в глобальний словник та FSMContext
    template_data[user_id] = {'channel_id': channel_id}
    await state.update_data(channel_id=channel_id)

    await Template.content.set()
    await callback_query.message.edit_text(
        f"Будь ласка, надішліть те, що ви хочете додати в шаблон:",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Назад", callback_data="back_to_my_post")
        )
    )
    
@dp.message_handler(state=Template.content, content_types=['text', 'photo', 'video', 'document'])
async def handle_content(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    channel_id = data.get('channel_id')

    content_type = message.content_type
    content_info = ""
    media_info = None
    media_type = None

    if content_type == 'text':
        content_info = message.text
        entities = message.entities 
        formated_content = format_entities(content_info, entities)
        await message.answer(f"{formated_content}", parse_mode='HTML', reply_markup=template_post(channel_id, template_data, user_id, template_data[user_id].get('url_buttons')))
        media_type = None
    elif content_type == 'photo':
        media_info = message.photo[-1].file_id
        await message.answer_photo(media_info, reply_markup=template_post(channel_id, template_data, user_id, template_data[user_id].get('url_buttons')))
        template_data[user_id]['media'] = media_info
        media_type = 'photo'
    elif content_type == 'video':
        media_info = message.video.file_id
        await message.answer_video(media_info, reply_markup=template_post(channel_id, template_data, user_id, template_data[user_id].get('url_buttons')))
        template_data[user_id]['media'] = media_info
        media_type = 'video'
    elif content_type == 'document':
        media_info = message.document.file_id
        await message.answer_document(media_info, reply_markup=template_post(channel_id, template_data, user_id, template_data[user_id].get('url_buttons')))
        template_data[user_id]['media'] = media_info
        media_type = 'document'
    else:
        await message.answer("Невідомий формат.")

    template_data[user_id]['content'] = formated_content
    await state.update_data(content=formated_content)
    template_data[user_id]['media'] = media_info
    template_data[user_id]['media_type'] = media_type

    await state.finish()

@dp.callback_query_handler(Text(startswith='templatemedia_'))
async def handle_media(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[-1]

    template_data[user_id]['channel_id'] = channel_id

    await Template.media.set()
    await callback_query.message.answer(
        "Будь ласка, надішліть медіа, яке ви хочете додати або змінити:",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Назад", callback_data="back_to_my_post")
        )
    )

@dp.message_handler(state=Template.media, content_types=['photo', 'video', 'document'])
async def handle_media_content(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channel_id = template_data[user_id]['channel_id']

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

    template_data[user_id]['media'] = media_info
    template_data[user_id]['media_type'] = media_type

    content_info = template_data[user_id].get('content')

    if media_info:
        if media_type == 'photo':
            await message.answer_photo(media_info, caption=f"{content_info}", parse_mode='HTML', reply_markup=template_post(channel_id, template_data, user_id, template_data[user_id].get('url_buttons')))
        elif media_type == 'video':
            await message.answer_video(media_info, caption=f"{content_info}", parse_mode='HTML', reply_markup=template_post(channel_id, template_data, user_id, template_data[user_id].get('url_buttons')))
        elif media_type == 'document':
            await message.answer_document(media_info, caption=f"{content_info}", parse_mode='HTML', reply_markup=template_post(channel_id, template_data, user_id, template_data[user_id].get('url_buttons')))
    else:
        await message.answer(f"{content_info}", parse_mode='HTML', reply_markup=template_post(channel_id, template_data, user_id, template_data[user_id].get('url_buttons')))

    await state.finish()

@dp.callback_query_handler(Text(startswith='templateadd_'))
async def handle_description(callback_query: types.CallbackQuery, state: FSMContext):
    await Template.description.set()
    await callback_query.message.answer(
        "Будь ласка, надішліть опис, який ви хочете додати або змінити:",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Назад", callback_data="back_to_my_post")
        )
    )

@dp.message_handler(state=Template.description, content_types=['text'])
async def handle_description_content(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channel_id = template_data[user_id]['channel_id']
    media_info = template_data[user_id].get('media')
    media_type = template_data[user_id].get('media_type')

    content_info = message.text
    entities = message.entities 
    formated_content = format_entities(content_info, entities)
    template_data[user_id]['content'] = formated_content
    
    if media_info:
        if media_type == 'photo':
            await message.answer_photo(media_info, caption=f"{content_info}", parse_mode='HTML', reply_markup=template_post(channel_id, template_data, user_id, template_data[user_id].get('url_buttons')))
        elif media_type == 'video':
            await message.answer_video(media_info, caption=f"{content_info}", parse_mode='HTML', reply_markup=template_post(channel_id, template_data, user_id, template_data[user_id].get('url_buttons')))
        elif media_type == 'document':
            await message.answer_document(media_info, caption=f"{content_info}", parse_mode='HTML', reply_markup=template_post(channel_id, template_data, user_id, template_data[user_id].get('url_buttons')))
    else:
        await message.answer(f"{content_info}", parse_mode='HTML', reply_markup=template_post(channel_id, template_data, user_id, template_data[user_id].get('url_buttons')))

    await state.finish()

@dp.callback_query_handler(Text(startswith='templateurl_buttons_'))
async def handle_url_buttons(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[-1]

    template_data[user_id]['channel_id'] = channel_id

    await Template.url_buttons.set()
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
        disable_web_page_preview=True 
    )


@dp.message_handler(state=Template.url_buttons, content_types=['text'])
async def handle_url_buttons_content(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channel_id = template_data[user_id]['channel_id']
    media_info = template_data[user_id].get('media')
    media_type = template_data[user_id].get('media_type')
    content_info = template_data[user_id].get('content')

    url_buttons_text = message.text
    url_buttons = parse_url_buttons(url_buttons_text)

    template_data[user_id]['url_buttons'] = url_buttons

    if media_info:
        if media_type == 'photo':
            await message.answer_photo(media_info, caption=f"{content_info}", parse_mode='HTML', reply_markup=template_post(channel_id, template_data, user_id, url_buttons))
        elif media_type == 'video':
            await message.answer_video(media_info, caption=f"{content_info}", parse_mode='HTML', reply_markup=template_post(channel_id, template_data, user_id, url_buttons))
        elif media_type == 'document':
            await message.answer_document(media_info, caption=f"{content_info}", parse_mode='HTML', reply_markup=template_post(channel_id, template_data, user_id, url_buttons))
    else:
        await message.answer(f"{content_info}", parse_mode='HTML', reply_markup=template_post(channel_id, template_data, user_id, url_buttons))

    await state.finish()
    
@dp.callback_query_handler(Text(startswith='save_template_'))
async def handle_schedule_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    data = callback_query.data.split('_')
    channel_id = data[2]

    media_info = template_data[user_id].get('media')
    media_type = template_data[user_id].get('media_type')
    content_info = template_data[user_id].get('content')
    url_buttons = template_data[user_id].get('url_buttons')


    media_path = None
    if media_info:
        file = await bot.get_file(media_info)
        original_file_name = file.file_path.split('/')[-1]

        media_dir = f'templates/{user_id}/'
        os.makedirs(media_dir, exist_ok=True)

        media_path = os.path.join(media_dir, original_file_name)

        try:
            await download_media(media_info, media_path)
        except TelegramAPIError as e:
            await callback_query.answer(f"Помилка завантаження медіа: {e}", show_alert=True)
            return
    url_buttons_str = str(url_buttons) if url_buttons else None
    save_template_to_db(user_id, channel_id, content_info, media_type, media_path, url_buttons_str)

    await callback_query.answer("Шаблон успішно збережено!", show_alert=True)
    await asyncio.sleep(1)
    await callback_query.message.delete()
    user_id = callback_query.from_user.id
    channels = get_user_channels(user_id)
    if not channels:
        add_channel_button = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("➕ Додати канал", callback_data="add_channel")
        )
        await callback_query.message.answer(no_channel_text, reply_markup=add_channel_button)
    else:
        channel_buttons = InlineKeyboardMarkup(row_width=2)
        for channel_id, channel_name in channels:
            channel_buttons.add(InlineKeyboardButton(channel_name, callback_data=f"create_template_{channel_id}"))
        channel_buttons.add(InlineKeyboardButton("Загальні", callback_data="general_templates"))
        
        await callback_query.message.answer("<b>ШАБЛОНИ:</b>\n\nЗберігайте шаблони для постів та рекламних креативів.\n\nВиберіть для якого каналу ви хочете переглянути шаблони", parse_mode='HTML', reply_markup=channel_buttons)



@dp.callback_query_handler(lambda c: c.data.startswith('template_'))
async def handle_template_selection(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    template_id = callback_query.data.split('_')[1]

    # Отримуємо шаблон з бази даних
    template = get_template_by_id(template_id)
    
    if not template:
        await callback_query.answer("Шаблон не знайдено.", show_alert=True)
        return

    post_id, user_id, channel_id, content, media_type, media_url, url_buttons_str = template

    try:
        url_buttons = ast.literal_eval(url_buttons_str) if url_buttons_str else []
    except (ValueError, SyntaxError) as e:
        print(f"Error unpacking url_buttons: {e}")
        url_buttons = []

    template_data[user_id] = {
        'post_id': post_id,
        'channel_id': channel_id,
        'media': media_url,
        'media_type': 'photo' if media_url and media_url.endswith(('.jpg', '.jpeg', '.png')) else 'video' if media_url else None,
        'content': content,
        'url_buttons': url_buttons
    }

    if media_type == 'photo' and media_url:
        media = InputFile(media_url) 
        await bot.send_photo(user_id, media, caption=content,  reply_markup=change_template_post(channel_id, template_data, user_id, post_id, url_buttons), parse_mode="HTML")
    elif media_type == 'video' and media_url:
        media = InputFile(media_url) 
        await bot.send_video(user_id, media, caption=content, reply_markup=change_template_post(channel_id, template_data, user_id, post_id, url_buttons), parse_mode="HTML")
    elif content:
        await bot.send_message(user_id, content,  reply_markup=change_template_post(channel_id, template_data, user_id, post_id, url_buttons), parse_mode="HTML")
    else:
        await callback_query.answer("Немає контенту для відображення.", show_alert=True)
        
        
@dp.callback_query_handler(lambda c: c.data.startswith('delete_template_post_'))
async def confirm_delete_post(callback_query: types.CallbackQuery):
    post_id = callback_query.data.split('_')[3]  
    channel_id = callback_query.data.split('_')[4] 
    user_id = callback_query.from_user.id  
    channel_name = get_channel_name_by_id(channel_id)
    confirmation_keyboard = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("✅ Так", callback_data=f"confirmtemplate_delete_{post_id}"),
        InlineKeyboardButton("❌ Ні", callback_data="canceltemplate_delete")
    )
    await callback_query.message.delete()
    await bot.send_message(
        chat_id=user_id,
        text=f"Ви впевнені, що хочете видалити шаблон для каналу {channel_name}?",
        reply_markup=confirmation_keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('confirmtemplate_delete_'))
async def delete_post(callback_query: types.CallbackQuery):
    post_id = callback_query.data.split('_')[-1] 
    user_id = callback_query.from_user.id  
    success = delete_template_from_db(user_id, post_id)
    if success:
        await callback_query.answer("Шаблон успішно видалено.", show_alert=True)
    else:
        await callback_query.answer("Не вдалося видалити шаблон. Будь ласка, спробуйте ще раз.", show_alert=True)
    await callback_query.message.delete()

@dp.callback_query_handler(lambda c: c.data == "canceltemplate_delete")
async def cancel_delete(callback_query: types.CallbackQuery):
    await callback_query.answer("Видалення шаблону скасовано.", show_alert=True)
    await callback_query.message.delete()
    
    
@dp.callback_query_handler(lambda c: c.data.startswith('publishtemplate_'))
async def handle_publish_template(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    post_id = callback_query.data.split('_')[1]
    channels = get_user_channels(user_id)

    if not channels:
        await callback_query.answer("У вас немає каналів для публікації.", show_alert=True)
        return

    keyboard = InlineKeyboardMarkup(row_width=1)
    for channel_id, channel_name in channels:
        keyboard.add(InlineKeyboardButton(channel_name, callback_data=f"publishonchannel_{post_id}_{channel_id}"))
    keyboard.add(InlineKeyboardButton("Назад", callback_data="back_to"))

    await callback_query.message.answer(
        "Оберіть канал для публікації поста:",
        reply_markup=keyboard
    )



@dp.callback_query_handler(lambda c: c.data.startswith('publishonchannel_'))
async def handle_template_selection(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    template_id = callback_query.data.split('_')[1]
    channel_id = callback_query.data.split('_')[2]

    # Отримуємо шаблон з бази даних
    await callback_query.message.delete()
    template = get_template_by_id(template_id)
    
    if not template:
        await callback_query.answer("Шаблон не знайдено.", show_alert=True)
        return

    post_id, user_id, channel_id, content, media_type, media_url, url_buttons_str = template

    try:
        url_buttons = ast.literal_eval(url_buttons_str) if url_buttons_str else []
    except (ValueError, SyntaxError) as e:
        print(f"Error unpacking url_buttons: {e}")
        url_buttons = []

    template_data[user_id] = {
        'post_id': post_id,
        'channel_id': channel_id,
        'media': media_url,
        'media_type': 'photo' if media_url and media_url.endswith(('.jpg', '.jpeg', '.png')) else 'video' if media_url else None,
        'content': content,
        'url_buttons': url_buttons
    }

    if media_type == 'photo' and media_url:
        media = InputFile(media_url) 
        await bot.send_photo(user_id, media, caption=content,  reply_markup=publish_template(channel_id, template_data, user_id, url_buttons), parse_mode="HTML")
    elif media_type == 'video' and media_url:
        media = InputFile(media_url) 
        await bot.send_video(user_id, media, caption=content, reply_markup=publish_template(channel_id, template_data, user_id, url_buttons), parse_mode="HTML")
    elif content:
        await bot.send_message(user_id, content, reply_markup=publish_template(channel_id, template_data, user_id, url_buttons), parse_mode="HTML")
    else:
        await callback_query.answer("Немає контенту для відображення.", show_alert=True)
        
        
        
        
        
##############################
####
####
###
###
##############################



@dp.callback_query_handler(Text(startswith='publishtemplatemedia_'))
async def handle_media(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[-1]

    # Оновлюємо дані в глобальному словнику
    template_data[user_id]['channel_id'] = channel_id

    await PublishTemplate.media.set()
    await callback_query.message.answer(
        "Будь ласка, надішліть медіа, яке ви хочете додати або змінити:",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Назад", callback_data="back_to_my_post")
        )
    )

@dp.message_handler(state=PublishTemplate.media, content_types=['photo', 'video', 'document'])
async def handle_media_content(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channel_id = template_data[user_id]['channel_id']

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

    template_data[user_id]['media'] = media_info
    template_data[user_id]['media_type'] = media_type
    
    

    content_info = template_data[user_id].get('content')
    keyboard = publish_template(channel_id, template_data, user_id, template_data[user_id].get('url_buttons'))

    if media_info:
        if media_type == 'photo':
            await message.answer_photo(media_info, caption=f"{content_info}",parse_mode='HTML', reply_markup=keyboard)
        elif media_type == 'video':
            await message.answer_video(media_info, caption=f"{content_info}", parse_mode='HTML',reply_markup=keyboard)
        elif media_type == 'document':
            await message.answer_document(media_info, caption=f"{content_info}",parse_mode='HTML', reply_markup=keyboard)
    else:
        await message.answer(f"{content_info}", reply_markup=keyboard)

    await state.finish()

@dp.callback_query_handler(Text(startswith='publishtemplateadd_'))
async def handle_description(callback_query: types.CallbackQuery, state: FSMContext):
    await PublishTemplate.description.set()
    await callback_query.message.answer(
        "Будь ласка, надішліть опис, який ви хочете додати або змінити:",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Назад", callback_data="back_to_my_post")
        )
    )

@dp.message_handler(state=PublishTemplate.description, content_types=['text'])
async def handle_description_content(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channel_id = template_data[user_id]['channel_id']
    media_info = template_data[user_id].get('media')
    media_type = template_data[user_id].get('media_type')

    content_info = message.text
    entities = message.entities 
    formated_content = format_entities(content_info, entities)
    template_data[user_id]['content'] = formated_content
    keyboard = publish_template(channel_id, template_data, user_id, template_data[user_id].get('url_buttons'))

    if media_info:
        if media_type == 'photo' and media_info:
            media = InputFile(media_info) 
            await message.answer_photo(media, caption=f"{content_info}", parse_mode='HTML', reply_markup=keyboard)
        elif media_type == 'video'and media_info:
            media = InputFile(media_info) 
            await message.answer_video(media, caption=f"{content_info}", parse_mode='HTML', reply_markup=keyboard)
        elif media_type == 'document'and media_info:
            media = InputFile(media_info) 
            await message.answer_document(media, caption=f"{content_info}", parse_mode='HTML', reply_markup=keyboard)
    else:
        await message.answer(f"{content_info}", parse_mode='HTML', reply_markup=keyboard)

    await state.finish()

@dp.callback_query_handler(Text(startswith='publishtemplateurl_buttons_'))
async def handle_url_buttons(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[-1]

    template_data[user_id]['channel_id'] = channel_id

    await PublishTemplate.url_buttons.set()
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
        disable_web_page_preview=True
    )


@dp.message_handler(state=PublishTemplate.url_buttons, content_types=['text'])
async def handle_url_buttons_content(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channel_id = template_data[user_id]['channel_id']
    media_info = template_data[user_id].get('media')
    media_type = template_data[user_id].get('media_type')
    content_info = template_data[user_id].get('content')

    url_buttons_text = message.text
    url_buttons = parse_url_buttons(url_buttons_text)

    template_data[user_id]['url_buttons'] = url_buttons
    keyboard = publish_template(channel_id, template_data, user_id, url_buttons)

    if media_info:
        if media_type == 'photo':
            await message.answer_photo(media_info, caption=f"{content_info}",parse_mode='HTML', reply_markup=keyboard)
        elif media_type == 'video':
            await message.answer_video(media_info, caption=f"{content_info}",parse_mode='HTML', reply_markup=keyboard)
        elif media_type == 'document':
            await message.answer_document(media_info, caption=f"{content_info}", parse_mode='HTML', reply_markup=keyboard)
    else:
        await message.answer(f"{content_info}", parse_mode='HTML', reply_markup=keyboard)

    await state.finish()


    
@dp.callback_query_handler(Text(startswith='templatecomments_'))
async def handle_comments(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = template_data[user_id]['channel_id']
    if 'comments' not in template_data[user_id]:
        template_data[user_id]['comments'] = 0 
    template_data[user_id]['comments'] = 1 if template_data[user_id]['comments'] == 0 else 0
    
    keyboard = publish_template(channel_id, template_data, user_id, template_data[user_id].get('url_buttons'))
    
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)


@dp.callback_query_handler(Text(startswith='templatepin_'))
async def handle_comments(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = template_data[user_id]['channel_id']
    if 'pin' not in template_data[user_id]:
        template_data[user_id]['pin'] = 0 
    template_data[user_id]['pin'] = 1 if template_data[user_id]['pin'] == 0 else 0
    
    keyboard = publish_template(channel_id, template_data, user_id, template_data[user_id].get('url_buttons'))
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)


@dp.callback_query_handler(Text(startswith='templatebell_'))
async def handle_comments(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = template_data[user_id]['channel_id']
    if 'bell' not in template_data[user_id]:
        template_data[user_id]['bell'] = 0 
    template_data[user_id]['bell'] = 1 if template_data[user_id]['bell'] == 0 else 0
    
    keyboard = publish_template(channel_id, template_data, user_id, template_data[user_id].get('url_buttons'))
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)
    
@dp.callback_query_handler(Text(startswith='templateaddpost_'))
async def handle_comments(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id =template_data[user_id]['channel_id']
    if 'addpost' not in template_data[user_id]:
        template_data[user_id]['addpost'] = 0  
    template_data[user_id]['addpost'] = 1 if template_data[user_id]['addpost'] == 0 else 0
    
    
    await callback_query.message.edit_reply_markup(reply_markup=publish_template_post(channel_id, template_data, user_id))

    
@dp.callback_query_handler(Text(startswith='templatenext_'))
async def handle_url_buttons(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[-1]
    channel_name = get_channel_name_by_id(channel_id)
    
    await callback_query.message.answer("<b>💼 НАЛАШТУВАННЯ ВІДПРАВКИ</b>\n\n"
                                           f"Пост готовий до публикації на каналі {channel_name}.", parse_mode='HTML', reply_markup=publish_template_post(channel_id, template_data, user_id))
    

    
    
@dp.callback_query_handler(Text(startswith='templatepublish_'))
async def confirm_publish(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[1] 
    confirm_keyboard = InlineKeyboardMarkup(row_width=2)
    confirm_keyboard.add(
        InlineKeyboardButton("✅ Так", callback_data=f"templateconfirm_publish_{channel_id}"),
        InlineKeyboardButton("❌ Ні", callback_data="templatecancel_publish")
    )

    await callback_query.message.edit_text("Ви впевнені, що хочете опублікувати пост?", reply_markup=confirm_keyboard)

@dp.callback_query_handler(Text(startswith='templateconfirm_publish_'))
async def handle_publish_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[-1]
    print(channel_id)

    media_info = template_data[user_id].get('media')
    media_type = template_data[user_id].get('media_type')
    content_info = template_data[user_id].get('content')
    url_buttons = template_data[user_id].get('url_buttons')

    bell = template_data[user_id].get('bell', 0)
    disable_notification = (bell == 0)
    pin_message = template_data[user_id].get('pin', 0) == 1
    post_id = template_data[user_id].get('post_id')

    if media_info:
        if media_type == 'photo':
            if media_info.startswith('templates'):
                media = InputFile(media_info)
                message = await bot.send_photo(channel_id, media, caption=content_info,parse_mode='HTML', reply_markup=post_shedule_keyboard(channel_id, template_data, user_id, url_buttons), disable_notification=disable_notification)
            else:
                message = await bot.send_photo(channel_id, media_info, caption=content_info,parse_mode='HTML', reply_markup=post_shedule_keyboard(channel_id, template_data, user_id, url_buttons), disable_notification=disable_notification)
        elif media_type == 'video':
            if media_info.startswith('templates'):
                media = InputFile(media_info)
                message = await bot.send_video(channel_id, media, caption=content_info,parse_mode='HTML', reply_markup=post_shedule_keyboard(channel_id, template_data, user_id, url_buttons), disable_notification=disable_notification)              
            else:
                message = await bot.send_video(channel_id, media_info, caption=content_info, parse_mode='HTML',reply_markup=post_shedule_keyboard(channel_id, template_data, user_id, url_buttons), disable_notification=disable_notification)
        elif media_type == 'document':
            if media_info.startswith('templates'):
                media = InputFile(media_info)
                message = await bot.send_document(channel_id, media, caption=content_info,parse_mode='HTML', reply_markup=post_shedule_keyboard(channel_id, template_data, user_id, url_buttons), disable_notification=disable_notification)              
            else:
                message = await bot.send_document(channel_id, media_info, caption=content_info,parse_mode='HTML', reply_markup=post_shedule_keyboard(channel_id, template_data, user_id, url_buttons), disable_notification=disable_notification)
                
    else:
        message = await bot.send_message(channel_id, content_info, parse_mode='HTML', reply_markup=post_shedule_keyboard(channel_id, template_data, user_id, url_buttons), disable_notification=disable_notification)

    if pin_message:
        await bot.pin_chat_message(channel_id, message.message_id)

    await callback_query.answer("Пост опубліковано!", show_alert=True)
    delete_post_from_db(user_id, post_id)
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
            channel_buttons.add(InlineKeyboardButton(channel_name, callback_data=f"create_template_{channel_id}"))
        channel_buttons.add(InlineKeyboardButton("Загальні", callback_data="general_templates"))

        await callback_query.message.edit_text(
            "<b>ШАБЛОНИ:</b>\n\nЗберігайте шаблони для постів та рекламних креативів.\n\nВиберіть для якого каналу ви хочете переглянути шаблони",
            parse_mode='HTML',
            reply_markup=channel_buttons
        )

@dp.callback_query_handler(Text(equals='templatecancel_publish'))
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
            channel_buttons.add(InlineKeyboardButton(channel_name, callback_data=f"create_template_{channel_id}"))
        channel_buttons.add(InlineKeyboardButton("Загальні", callback_data="general_templates"))

        await callback_query.message.edit_text(
            "<b>ШАБЛОНИ:</b>\n\nЗберігайте шаблони для постів та рекламних креативів.\n\nВиберіть для якого каналу ви хочете переглянути шаблони",
            parse_mode='HTML',
            reply_markup=channel_buttons
        )

        
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
                
def register_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(handle_create_template, lambda c: c.data == 'add_channel')