from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext, Dispatcher
from main import bot, dp
from states.user_states import SheduleForm
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from keyboards.user_keyboards import *
from data.texts import *
from database.user_db import *
import asyncio, re, os, logging
from aiogram.utils.exceptions import TelegramAPIError, BadRequest
from datetime import datetime
import locale
import datetime
from aiogram.types import InputFile
from functions.user_functions import *
import ast 

# locale.setlocale(locale.LC_TIME, 'uk_UA.UTF-8')  
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


change_user_data = {}

@dp.callback_query_handler(lambda c: c.data.startswith('date_'))
async def handle_date_selection(callback_query: types.CallbackQuery):
    selected_date_str = callback_query.data.split('_')[1]
    selected_date = datetime.datetime.strptime(selected_date_str, "%Y-%m-%d").date()

    user_id = callback_query.from_user.id
    current_date = datetime.datetime.today()
    scheduled_dates = get_scheduled_times(user_id)
    calendar_buttons = generate_calendar(current_date, scheduled_dates)
    posts = get_posts_for_date(user_id, selected_date)
    if user_id not in change_user_data:
        change_user_data[user_id] = {}

    if not posts:
        await bot.edit_message_text(
            text=f"На <b>{selected_date.strftime('%A')}, {selected_date.strftime('%d')} {selected_date.strftime('%B')} {selected_date.strftime('%Y')}</b> не заплановано ні одного поста.",
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=calendar_buttons,
            parse_mode='HTML'
        )
    else:
        for post in posts:
            post_id = post.get('id')
            channel_id = post.get('channel_id')
            print(channel_id)
            content = post.get('content') if 'content' in post else None
            media_url = post.get('media_path') if 'media_path' in post else None
            media_type = post.get('media_type') if 'media_type' in post else None
            url_buttons_str = post.get('url_buttons') if 'url_buttons' in post else None
            scheduled_time = post.get('scheduled_time')

            try:
                url_buttons = ast.literal_eval(url_buttons_str) if url_buttons_str else []
            except (ValueError, SyntaxError) as e:
                print(f"Error unpacking url_buttons: {e}")
                url_buttons = []
           
            change_user_data[user_id]['post_id'] = post_id
            change_user_data[user_id]['channel_id'] = channel_id
            change_user_data[user_id]['media'] = media_url
            change_user_data[user_id]['media_type'] = 'photo' if media_url and media_url.endswith(('.jpg', '.jpeg', '.png')) else 'video' if media_url else None
            change_user_data[user_id]['content'] = content
            change_user_data[user_id]['url_buttons'] = url_buttons

            
            if media_type == 'photo' and media_url:
                media = InputFile(media_url) 
                await bot.send_photo(user_id, media, caption=content, reply_markup=change_shedule_post(channel_id, change_user_data, user_id, post_id, url_buttons), parse_mode="HTML")
            elif media_type == 'video' and media_url:
                media = InputFile(media_url) 
                await bot.send_video(user_id, media, caption=content, reply_markup=change_shedule_post(channel_id, change_user_data, user_id, post_id, url_buttons), parse_mode="HTML")
            elif content:
                await bot.send_message(user_id, content, reply_markup=change_shedule_post(channel_id, change_user_data, user_id, post_id, url_buttons), parse_mode="HTML")



@dp.callback_query_handler(lambda c: c.data.startswith('sheduleddate_'))
async def handle_date_selection(callback_query: types.CallbackQuery):
    selected_datetime_str = callback_query.data.split('_')[1]
    selected_datetime = datetime.datetime.strptime(selected_datetime_str, '%Y-%m-%d %H:%M')
    print(selected_datetime)
    user_id = callback_query.from_user.id
    current_date = datetime.datetime.today()
    scheduled_dates = get_scheduled_times(user_id)
    calendar_buttons = generate_calendar(current_date, scheduled_dates)
    posts = get_sheduled_posts_for_date(user_id, selected_datetime)
    if user_id not in change_user_data:
        change_user_data[user_id] = {}

    if not posts:
        await bot.edit_message_text(
            text=f"На <b>{selected_datetime.strftime('%A')}, {selected_datetime.strftime('%d')} {selected_datetime.strftime('%B')} {selected_datetime.strftime('%Y')} {selected_datetime.strftime('%H:%M')}</b> не заплановано ні одного поста.",
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=calendar_buttons,
            parse_mode='HTML'
        )
    else:
        for post in posts:
            post_id = post.get('id')
            channel_id = post.get('channel_id')
            print(channel_id)
            content = post.get('content') if 'content' in post else None
            media_url = post.get('media_path') if 'media_path' in post else None
            media_type = post.get('media_type') if 'media_type' in post else None
            url_buttons_str = post.get('url_buttons') if 'url_buttons' in post else None
            scheduled_time = post.get('scheduled_time')

            try:
                url_buttons = ast.literal_eval(url_buttons_str) if url_buttons_str else []
            except (ValueError, SyntaxError) as e:
                print(f"Error unpacking url_buttons: {e}")
                url_buttons = []

            change_user_data[user_id]['post_id'] = post_id
            change_user_data[user_id]['channel_id'] = channel_id
            change_user_data[user_id]['media'] = media_url
            change_user_data[user_id]['media_type'] = 'photo' if media_url and media_url.endswith(('.jpg', '.jpeg', '.png')) else 'video' if media_url else None
            change_user_data[user_id]['content'] = content
            change_user_data[user_id]['url_buttons'] = url_buttons

            if media_type == 'photo' and media_url:
                media = InputFile(media_url)
                await bot.send_photo(user_id, media, caption=content, reply_markup=change_shedule_post(channel_id, change_user_data, user_id, post_id, url_buttons), parse_mode="HTML")
            elif media_type == 'video' and media_url:
                media = InputFile(media_url)
                await bot.send_video(user_id, media, caption=content, reply_markup=change_shedule_post(channel_id, change_user_data, user_id, post_id, url_buttons), parse_mode="HTML")
            elif content:
                await bot.send_message(user_id, content, reply_markup=change_shedule_post(channel_id, change_user_data, user_id, post_id, url_buttons), parse_mode="HTML")
   
@dp.callback_query_handler(lambda c: c.data.startswith('delete_shedule_post_'))
async def confirm_delete_post(callback_query: types.CallbackQuery):
    post_id = callback_query.data.split('_')[3]  
    channel_id = callback_query.data.split('_')[4] 
    user_id = callback_query.from_user.id  
    channel_name = get_channel_name_by_id(channel_id)
    confirmation_keyboard = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("✅ Так", callback_data=f"confirm_delete_{post_id}"),
        InlineKeyboardButton("❌ Ні", callback_data="cancel_delete")
    )
    
    await callback_query.message.delete()

    await bot.send_message(
        chat_id=user_id,
        text=f"Ви впевнені, що хочете видалити запланований пост на канал {channel_name}?",
        reply_markup=confirmation_keyboard
    )


@dp.callback_query_handler(lambda c: c.data.startswith('confirm_delete_'))
async def delete_post(callback_query: types.CallbackQuery):
    post_id = callback_query.data.split('_')[2] 
    user_id = callback_query.from_user.id  

    # Call the updated function to get success status and media path
    success, media_path = delete_post_from_db(user_id, post_id)

    if success:
        if media_path and os.path.exists(media_path):  # Check if the media file exists
            try:
                os.remove(media_path)  # Delete the media file
                await callback_query.answer("Пост і медіа успішно видалено.", show_alert=True)
            except Exception as e:
                await callback_query.answer("Пост видалено, але не вдалося видалити медіа.", show_alert=True)
        else:
            await callback_query.answer("Пост успішно видалено, медіа не знайдено.", show_alert=True)
    else:
        await callback_query.answer("Не вдалося видалити пост. Будь ласка, спробуйте ще раз.", show_alert=True)
        
    await callback_query.message.delete()


@dp.callback_query_handler(lambda c: c.data == "cancel_delete")
async def cancel_delete(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    await callback_query.answer("Видалення поста скасовано.", show_alert=True)
    await callback_query.message.delete()


@dp.callback_query_handler(Text(startswith='shedule_next_'))
async def handle_url_buttons(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[-1]
    channel_name = get_channel_name_by_id(channel_id)
    
    await callback_query.message.answer("<b>💼 НАЛАШТУВАННЯ ВІДПРАВКИ</b>\n\n"
                                           f"Пост готовий до публікації на каналі {channel_name}.", parse_mode='HTML', reply_markup=publish_post(channel_id, change_user_data, user_id))
    
        
        
@dp.callback_query_handler(Text(startswith='shedulemedia_'))
async def handle_media(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[-1]

    # Оновлюємо дані в глобальному словнику
    change_user_data[user_id]['channel_id'] = channel_id

    await SheduleForm.media.set()
    await callback_query.message.answer(
        "Будь ласка, надішліть медіа, яке ви хочете додати або змінити:",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Назад", callback_data="back_to_my_post")
        )
    )

@dp.message_handler(state=SheduleForm.media, content_types=['photo', 'video', 'document'])
async def handle_media_content(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channel_id = change_user_data[user_id]['channel_id']

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

    change_user_data[user_id]['media'] = media_info
    change_user_data[user_id]['media_type'] = media_type
    
    

    content_info = change_user_data[user_id].get('content')
    post_id = change_user_data[user_id].get('post_id')
    keyboard = change_shedule_post(channel_id, change_user_data, user_id, post_id,  change_user_data[user_id].get('url_buttons'))

    if media_info:
        if media_type == 'photo':
            await message.answer_photo(media_info, caption=f"{content_info}", parse_mode="HTML", reply_markup=keyboard)
        elif media_type == 'video':
            await message.answer_video(media_info, caption=f"{content_info}", parse_mode="HTML", reply_markup=keyboard)
        elif media_type == 'document':
            await message.answer_document(media_info, caption=f"{content_info}", parse_mode="HTML", reply_markup=keyboard)
    else:
        await message.answer(f"{content_info}", parse_mode="HTML", reply_markup=keyboard)

    await state.finish()
    
    
    
@dp.callback_query_handler(Text(startswith='sheduleadd_'))
async def handle_description(callback_query: types.CallbackQuery, state: FSMContext):
    await SheduleForm.description.set()
    await callback_query.message.answer(
        "Будь ласка, надішліть опис, який ви хочете додати або змінити:",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Назад", callback_data="back_to_my_post")
        )
    )

@dp.message_handler(state=SheduleForm.description, content_types=['text'])
async def handle_description_content(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channel_id = change_user_data[user_id]['channel_id']
    media_info = change_user_data[user_id].get('media')
    media_type = change_user_data[user_id].get('media_type')

    # Форматування сутностей тексту
    content_info = message.text
    entities = message.entities 
    formatted_content = format_entities(content_info, entities)  # Форматуємо текст із сутностями

    # Оновлюємо опис у глобальному словнику з форматованим контентом
    change_user_data[user_id]['content'] = formatted_content
    post_id = change_user_data[user_id].get('post_id')

    # Створюємо клавіатуру для посту
    keyboard = change_shedule_post(
        channel_id,
        change_user_data,
        user_id,
        post_id,
        change_user_data[user_id].get('url_buttons')
    )

    if media_info:
        if media_type == 'photo':
            if media_info.startswith('posts'):
                media = InputFile(media_info)
                await message.answer_photo(media, caption=f"{formatted_content}", parse_mode="HTML", reply_markup=keyboard)
            else:
                await message.answer_photo(media_info, caption=f"{formatted_content}", parse_mode="HTML", reply_markup=keyboard)
        elif media_type == 'video':
            if media_info.startswith('posts'):
                media = InputFile(media_info)
                await message.answer_video(media, caption=f"{formatted_content}", parse_mode="HTML", reply_markup=keyboard)          
            else:
                await message.answer_video(media_info, caption=f"{formatted_content}", parse_mode="HTML", reply_markup=keyboard)
        elif media_type == 'document':
            if media_info.startswith('posts'):
                media = InputFile(media_info)
                await message.answer_document(media, caption=f"{formatted_content}", parse_mode="HTML", reply_markup=keyboard)          
            else:
                await message.answer_document(media_info, caption=f"{formatted_content}", parse_mode="HTML", reply_markup=keyboard)    
    else:
        await message.answer(f"{formatted_content}", parse_mode="HTML", reply_markup=keyboard)

    # Завершуємо стан
    await state.finish()

@dp.callback_query_handler(Text(startswith='sheduleurl_buttons_'))
async def handle_url_buttons(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[-1]

    change_user_data[user_id]['channel_id'] = channel_id

    await SheduleForm.url_buttons.set()
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


@dp.message_handler(state=SheduleForm.url_buttons, content_types=['text'])
async def handle_url_buttons_content(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channel_id = change_user_data[user_id]['channel_id']
    media_info = change_user_data[user_id].get('media')
    media_type = change_user_data[user_id].get('media_type')
    content_info = change_user_data[user_id].get('content')

    url_buttons_text = message.text
    url_buttons = parse_url_buttons(url_buttons_text)

    change_user_data[user_id]['url_buttons'] = url_buttons
    post_id = change_user_data[user_id].get('post_id')
    keyboard = change_shedule_post(channel_id, change_user_data, user_id, post_id, url_buttons)
    
    if media_info:
        if media_type == 'photo':
            if media_info.startswith('posts'):
                media = InputFile(media_info)
                await message.answer_photo(media, caption=f"{content_info}", parse_mode="HTML", reply_markup=keyboard)
            else:
                await message.answer_photo(media_info, caption=f"{content_info}", parse_mode="HTML", reply_markup=keyboard)
        elif media_type == 'video':
            if media_info.startswith('posts'):
                media = InputFile(media_info)
                await message.answer_video(media, caption=f"{content_info}", parse_mode="HTML", reply_markup=keyboard)          
            else:
                await message.answer_video(media_info, caption=f"{content_info}", parse_mode="HTML", reply_markup=keyboard)
        elif media_type == 'document':
            if media_info.startswith('posts'):
                media = InputFile(media_info)
                await message.answer_document(media, caption=f"{content_info}", parse_mode="HTML", reply_markup=keyboard)          
            else:
                await message.answer_document(media_info, caption=f"{content_info}", parse_mode="HTML", reply_markup=keyboard)    
    else:
        await message.answer(f"{content_info}", parse_mode="HTML", reply_markup=keyboard)

    await state.finish()


    
@dp.callback_query_handler(Text(startswith='shedulecomments_'))
async def handle_comments(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = change_user_data[user_id]['channel_id']
    if 'comments' not in change_user_data[user_id]:
        change_user_data[user_id]['comments'] = 0 
    change_user_data[user_id]['comments'] = 1 if change_user_data[user_id]['comments'] == 0 else 0
    
    post_id = change_user_data[user_id].get('post_id')
    keyboard = change_shedule_post(channel_id, change_user_data, user_id, post_id,  change_user_data[user_id].get('url_buttons'))
    
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)


@dp.callback_query_handler(Text(startswith='shedulepin_'))
async def handle_comments(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = change_user_data[user_id]['channel_id']
    if 'pin' not in change_user_data[user_id]:
        change_user_data[user_id]['pin'] = 0 
    change_user_data[user_id]['pin'] = 1 if change_user_data[user_id]['pin'] == 0 else 0
    
    post_id = change_user_data[user_id].get('post_id')
    keyboard = change_shedule_post(channel_id, change_user_data, user_id, post_id,  change_user_data[user_id].get('url_buttons'))
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)


@dp.callback_query_handler(Text(startswith='shedulebell_'))
async def handle_comments(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = change_user_data[user_id]['channel_id']
    if 'bell' not in change_user_data[user_id]:
        change_user_data[user_id]['bell'] = 0 
    change_user_data[user_id]['bell'] = 1 if change_user_data[user_id]['bell'] == 0 else 0
    
    post_id = change_user_data[user_id].get('post_id')
    keyboard = change_shedule_post(channel_id, change_user_data, user_id, post_id,  change_user_data[user_id].get('url_buttons'))
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)
    
@dp.callback_query_handler(Text(startswith='sheduleaddpost_'))
async def handle_comments(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id =change_user_data[user_id]['channel_id']
    if 'addpost' not in change_user_data[user_id]:
        change_user_data[user_id]['addpost'] = 0  
    change_user_data[user_id]['addpost'] = 1 if change_user_data[user_id]['addpost'] == 0 else 0
    
    
    await callback_query.message.edit_reply_markup(reply_markup=publish_shedule_post(channel_id, change_user_data, user_id))

    
@dp.callback_query_handler(Text(startswith='shedulenext_'))
async def handle_url_buttons(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[-1]
    channel_name = get_channel_name_by_id(channel_id)
    
    await callback_query.message.answer("<b>💼 НАЛАШТУВАННЯ ВІДПРАВКИ</b>\n\n"
                                           f"Пост готовий до публикації на каналі {channel_name}.", parse_mode='HTML', reply_markup=publish_shedule_post(channel_id, change_user_data, user_id))
    
    
@dp.callback_query_handler(Text(startswith='sheduletimer_back'), state=SheduleForm.schedule_post)
async def handle_url_buttons(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[-1]
    channel_name = get_channel_name_by_id(channel_id)
    await state.finish()
    
    await callback_query.message.edit_text("<b>💼 НАЛАШТУВАННЯ ВІДПРАВКИ</b>\n\n"
                                           f"Пост готовий до публикації на каналі {channel_name}.", parse_mode='HTML', reply_markup=publish_shedule_post(channel_id, change_user_data, user_id))
    
  
    
    
@dp.callback_query_handler(Text(startswith='shedulepublish_'))
async def confirm_publish(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[1] 
    confirm_keyboard = InlineKeyboardMarkup(row_width=2)
    confirm_keyboard.add(
        InlineKeyboardButton("✅ Так", callback_data=f"sheduleconfirm_publish_{channel_id}"),
        InlineKeyboardButton("❌ Ні", callback_data="shedulecancel_publish")
    )

    await callback_query.message.edit_text("Ви впевнені, що хочете опублікувати пост?", reply_markup=confirm_keyboard)

@dp.callback_query_handler(Text(startswith='sheduleconfirm_publish_'))
async def handle_publish_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[-1]  
    print(channel_id)

    media_info = change_user_data[user_id].get('media')
    media_type = change_user_data[user_id].get('media_type')
    content_info = change_user_data[user_id].get('content')
    url_buttons = change_user_data[user_id].get('url_buttons')

    bell = change_user_data[user_id].get('bell', 0)
    disable_notification = (bell == 0) 
    pin_message = change_user_data[user_id].get('pin', 0) == 1 
    post_id = change_user_data[user_id].get('post_id')
    
    if media_info:
        if media_type == 'photo':
            if media_info.startswith('posts'):
                media = InputFile(media_info)
                message = await bot.send_photo(channel_id, media, caption=content_info, parse_mode="HTML", reply_markup=post_shedule_keyboard(channel_id, change_user_data, user_id, url_buttons), disable_notification=disable_notification)
            else:
                message = await bot.send_photo(channel_id, media_info, caption=content_info, parse_mode="HTML", reply_markup=post_shedule_keyboard(channel_id, change_user_data, user_id, url_buttons), disable_notification=disable_notification)
        elif media_type == 'video':
            if media_info.startswith('posts'):
                media = InputFile(media_info)
                message = await bot.send_video(channel_id, media, caption=content_info, parse_mode="HTML", reply_markup=post_shedule_keyboard(channel_id, change_user_data, user_id, url_buttons), disable_notification=disable_notification)              
            else:
                message = await bot.send_document(channel_id, media_info, caption=content_info, parse_mode="HTML", reply_markup=post_shedule_keyboard(channel_id, change_user_data, user_id, url_buttons), disable_notification=disable_notification)
        elif media_type == 'document':
            if media_info.startswith('posts'):
                media = InputFile(media_info)
                message = await bot.send_document(channel_id, media, caption=content_info, parse_mode="HTML", reply_markup=post_shedule_keyboard(channel_id, change_user_data, user_id, url_buttons), disable_notification=disable_notification)              
            else:
                message = await bot.send_message(channel_id, content_info, parse_mode="HTML", reply_markup=post_shedule_keyboard(channel_id, change_user_data, user_id, url_buttons), disable_notification=disable_notification)
                
    else:
        message = await bot.send_message(channel_id, content_info, parse_mode="HTML", reply_markup=post_shedule_keyboard(channel_id, change_user_data, user_id, url_buttons), disable_notification=disable_notification)

    if pin_message:
        await bot.pin_chat_message(channel_id, message.message_id)

    await callback_query.answer("Пост опубліковано!", show_alert=True)
    # delete_post_from_db(user_id, post_id)
    await asyncio.sleep(2) 
    channels = get_user_channels(user_id)
    if not channels:
        add_channel_button = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("➕ Додати канал", callback_data="add_channel")
        )
        await callback_query.message.edit_text(no_channel_text, reply_markup=add_channel_button)
    else:
        current_date = datetime.datetime.today()
        scheduled_dates = get_scheduled_times(user_id)  
        calendar_buttons = generate_calendar(current_date, scheduled_dates) 

        await callback_query.message.edit_text("<b>КОНТЕНТ ПЛАН:</b>\n\nВ цьому розділі ви можете переглядати и редагувати заплановані пости.", parse_mode='HTML', reply_markup=calendar_buttons)


@dp.callback_query_handler(Text(equals='shedulecancel_publish'))
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
        current_date = datetime.datetime.today()
        scheduled_dates = get_scheduled_times(user_id)  
        calendar_buttons = generate_calendar(current_date, scheduled_dates) 

        await callback_query.message.edit_text("<b>КОНТЕНТ ПЛАН:</b>\n\nВ цьому розділі ви можете переглядати и редагувати заплановані пости.", parse_mode='HTML', reply_markup=calendar_buttons)
        


@dp.callback_query_handler(Text(startswith='sheduletimer_'))
async def handle_timer(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[-1]
    
    back_keyboard = InlineKeyboardMarkup(row_width=2)
    back_keyboard.add(InlineKeyboardButton("◀️ Назад", callback_data=f"sheduletimer_back{channel_id}"))

    await SheduleForm.schedule_post.set() 
    await callback_query.message.edit_text(
        "<b>🕔 ВІДКЛАДЕНИЙ ПОСТ</b>\n\n"
        "Відправте час публікування вашого поста (GMT+2 Київ) в форматі (DD.MM.YYYY HH:MM), наприклад:\n\n"
        "<code>02.10.2024 12:00\n"
        "23.05.2025 05:30</code>", 
        parse_mode='HTML', reply_markup=back_keyboard
    )

@dp.message_handler(state=SheduleForm.schedule_post)
async def process_schedule_post(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channel_id = change_user_data[user_id].get('channel_id')
    channel_name = get_channel_name_by_id(channel_id)

    date_pattern = r'^\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}$'
    
    if re.match(date_pattern, message.text):
        try:
            scheduled_time = datetime.datetime.strptime(message.text, "%d.%m.%Y %H:%M")
            
            if scheduled_time < datetime.datetime.now():
                await message.answer("Вибачте, але ви не можете запланувати пост у минулому. Спробуйте ще раз.")
                return
            
            confirmation_text = (
                f"Запланувати пост в канал <b>{channel_name}</b> "
                f"на {scheduled_time.strftime('%A, %d %B %Y')} "
                f"в {scheduled_time.strftime('%H:%M')}?"
            )

            confirm_keyboard = InlineKeyboardMarkup(row_width=1)
            confirm_keyboard.add(
                InlineKeyboardButton("✅ Так, запланувати", callback_data=f"sheduleconfirm_schedule_{channel_id}_{scheduled_time.timestamp()}"),
                InlineKeyboardButton("◀️ Назад", callback_data=f"shedulenext_{channel_id}")
            )

            await message.answer(confirmation_text, parse_mode='HTML', reply_markup=confirm_keyboard)
            await state.finish() 
        except ValueError:
            await message.answer("Неправильний формат дати. Спробуйте ще раз.")
    else:
        await message.answer("Неправильний формат. Використовуйте (DD.MM.YYYY HH:MM).")
    
     
@dp.callback_query_handler(Text(startswith='sheduleconfirm_schedule_'))
async def handle_schedule_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    data = callback_query.data.split('_')
    channel_id = data[2]
    scheduled_time = datetime.datetime.fromtimestamp(float(data[3]))

    media_info = change_user_data[user_id].get('media')
    media_type = change_user_data[user_id].get('media_type')
    content_info = change_user_data[user_id].get('content')
    url_buttons = change_user_data[user_id].get('url_buttons')
    bell = change_user_data[user_id].get('bell', 0)
    pin = change_user_data[user_id].get('pin', 0)
    post_id = change_user_data[user_id].get('post_id')

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
    url_buttons_str = str(url_buttons) if url_buttons else None
    delete_post_from_db(user_id, post_id)
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
        current_date = datetime.datetime.today()
        scheduled_dates = get_scheduled_times(user_id)
        calendar_buttons = generate_calendar(current_date, scheduled_dates)  

        await callback_query.message.edit_text("<b>КОНТЕНТ ПЛАН:</b>\n\nВ цьому розділі ви можете переглядати и редагувати заплановані пости.", parse_mode='HTML', reply_markup=calendar_buttons)

        
        
@dp.callback_query_handler(Text(startswith='shedulepost_save_'))
async def confirm_publish(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    post_id = callback_query.data.split('_')[2] 
    channel_id = callback_query.data.split('_')[-1] 
    channel_name = get_channel_name_by_id(channel_id)
    confirm_keyboard = InlineKeyboardMarkup(row_width=2)
    confirm_keyboard.add(
        InlineKeyboardButton("✅ Так", callback_data=f"confirmshedulepost_save_{post_id}_{channel_id}"),
        InlineKeyboardButton("❌ Ні", callback_data="back_to")
    )

    await callback_query.message.answer(f"Ви впевнені, що хочете змінити запланований пост на канал {channel_name}?", reply_markup=confirm_keyboard)
    
    
@dp.callback_query_handler(Text(startswith='confirmshedulepost_save_'))
async def handle_schedule_confirmation(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data.split('_')
    channel_id = data[3]
    post_id = data[2]

    media_info = change_user_data[user_id].get('media')
    media_type = change_user_data[user_id].get('media_type')
    content_info = change_user_data[user_id].get('content')
    url_buttons = change_user_data[user_id].get('url_buttons')
    bell = change_user_data[user_id].get('bell', 0)
    pin = change_user_data[user_id].get('pin', 0)

    media_path = None
    if media_info:
        
        try:
            file = await bot.get_file(media_info)
            original_file_name = file.file_path.split('/')[-1]

            media_dir = f'posts/{user_id}/'
            os.makedirs(media_dir, exist_ok=True)

            media_path = os.path.join(media_dir, original_file_name)
            await download_media(media_info, media_path)
            url_buttons_str = str(url_buttons) if url_buttons else None
            update_post_in_db(post_id, user_id, channel_id, content_info, media_type, media_path, url_buttons_str, bell, pin)
        except BadRequest as e:
            media_path = None  
            url_buttons_str = str(url_buttons) if url_buttons else None
            update_post_in_db_without_photo(post_id, user_id, channel_id, content_info, url_buttons_str, bell, pin)

    
    await callback_query.answer("Запланований пост успішно змінено!", show_alert=True)
    await asyncio.sleep(2)
    channels = get_user_channels(user_id)
    if not channels:
        add_channel_button = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("➕ Додати канал", callback_data="add_channel")
        )
        await callback_query.message.edit_text(no_channel_text, reply_markup=add_channel_button)
    else:
        current_date = datetime.datetime.today()
        scheduled_dates = get_scheduled_times(user_id)  
        calendar_buttons = generate_calendar(current_date, scheduled_dates) 

        await callback_query.message.edit_text("<b>КОНТЕНТ ПЛАН:</b>\n\nВ цьому розділі ви можете переглядати и редагувати заплановані пости.", parse_mode='HTML', reply_markup=calendar_buttons)



@dp.callback_query_handler(Text(equals="all_scheduled"))
async def handle_all_scheduled_posts(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    channels = get_user_channels(user_id)
    if not channels:
        add_channel_button = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("➕ Додати канал", callback_data="add_channel"),
            InlineKeyboardButton(text="← Назад", callback_data="back_to_schedule_menu")
        )
        
        await callback_query.message.edit_text(no_channel_text, reply_markup=add_channel_button)
    else:
        channel_buttons = InlineKeyboardMarkup(row_width=2)
        for channel_id, channel_name in channels:
            channel_buttons.add(InlineKeyboardButton(channel_name, callback_data=f"scheduled_for_{channel_id}"))
        channel_buttons.add(InlineKeyboardButton(text="← Назад", callback_data="back_to_schedule_menu"))
        
        await callback_query.message.edit_text("Виберіть канал на якому бажаєте переглянути відкладені пости:", reply_markup=channel_buttons)
        
        
    # posts = get_scheduled_posts(user_id)
    
    # back_keyboard = InlineKeyboardMarkup(row_width=1)
    # back_keyboard.add(InlineKeyboardButton(text="← Назад", callback_data="back_to_schedule_menu"))

    # if not posts:
    #     await callback_query.message.edit_text("Немає відкладених постів:", reply_markup=back_keyboard)
    #     return
    # keyboard = InlineKeyboardMarkup(row_width=1)
    # for post in posts:
    #     channel_id = post[0]
        
    #     scheduled_time = post[1]
    #     if isinstance(scheduled_time, str):
    #         try:
    #             scheduled_time = datetime.datetime.strptime(scheduled_time, '%Y-%m-%d %H:%M:%S')
    #         except ValueError:
    #             scheduled_time = datetime.datetime.strptime(scheduled_time, '%Y-%m-%d %H:%M')  # Якщо формат без секунд

    #     button_text = f"{get_channel_name_by_id(channel_id)[:8]}, {scheduled_time.strftime('%m-%d %H:%M')}"
    #     keyboard.add(InlineKeyboardButton(text=button_text, callback_data=f"date_{scheduled_time.strftime('%Y-%m-%d')}"))

    # keyboard.add(InlineKeyboardButton(text="← Назад", callback_data="back_to_schedule_menu"))

    # await callback_query.message.edit_text("Відкладені пости:", reply_markup=keyboard)
    
    
    
@dp.callback_query_handler(Text(startswith="scheduled_for"))
async def handle_all_scheduled_posts(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[-1] 
    channel_name = get_channel_name_by_id(channel_id)
    posts = get_scheduled_posts(user_id, channel_id)
    
    back_keyboard = InlineKeyboardMarkup(row_width=1)
    back_keyboard.add(InlineKeyboardButton(text="← Назад", callback_data="all_scheduled"))

    if not posts:
        await callback_query.message.edit_text("Немає відкладених постів:", reply_markup=back_keyboard)
        return

    keyboard = InlineKeyboardMarkup(row_width=1)
    for post in posts:
        channel_id = post[0]
        content = post[1]
        scheduled_time = post[2]
        posted = post[3]

        if isinstance(scheduled_time, str):
            try:
                scheduled_time = datetime.datetime.strptime(scheduled_time, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                scheduled_time = datetime.datetime.strptime(scheduled_time, '%Y-%m-%d')  # Format without seconds

        # Determine the post status symbol
        status_symbol = "✅" if posted == 1 else "⏳"
        
        # Remove HTML tags from content
        content_cleaned = re.sub(r'<[^>]*>', '', content)  # Regex to remove HTML tags
        
        # Extract the first few words from the cleaned content
        content_preview = ' '.join(content_cleaned.split()[:3])  # Get the first 5 words
        button_text = f"{status_symbol} {content_preview}, {scheduled_time.strftime('%d.%m %H:%M')}"

        keyboard.add(InlineKeyboardButton(text=button_text, callback_data=f"sheduleddate_{scheduled_time.strftime('%Y-%m-%d %H:%M')}"))

    keyboard.add(InlineKeyboardButton(text="← Назад", callback_data="all_scheduled"))

    await callback_query.message.edit_text(f"Відкладені пости для каналу <b>{channel_name}</b>:", parse_mode='HTML', reply_markup=keyboard)

    
@dp.callback_query_handler(Text(equals="back_to_schedule_menu"))
async def handle_back_to_schedule_menu(callback_query: types.CallbackQuery):
    current_date = datetime.datetime.today()
    user_id = callback_query.from_user.id
    scheduled_dates = get_scheduled_times(user_id)  # Ваш метод для отримання дат
    calendar_buttons = generate_calendar(current_date, scheduled_dates)  # Генерація календаря

    # Повернення до меню "Контент план"
    await callback_query.message.edit_text(
        "<b>КОНТЕНТ ПЛАН:</b>\n\nВ цьому розділі ви можете переглядати и редагувати заплановані пости.",
        parse_mode='HTML',
        reply_markup=calendar_buttons
    )

    
    
def register_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(handle_date_selection, lambda c: c.data == 'add_channel')