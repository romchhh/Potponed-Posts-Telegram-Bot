from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext, Dispatcher
from main import bot, dp
from states.user_states import EditPostState
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from keyboards.user_keyboards import *
from data.texts import *
from database.user_db import *
from functions.user_functions import *





change_user_data = {}

@dp.message_handler(state=EditPostState.waiting_for_post, content_types=types.ContentType.ANY)
async def handle_forwarded_post(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if message.text in ["Створити пост", "Редагувати пост", "Контент план", "Налаштування", "Шаблони"]:
        await state.finish()  # Завершуємо стан
        return

    if message.forward_from_chat:
        channel_id = message.forward_from_chat.id

        if is_channel_in_db(channel_id):
            user_data = await state.get_data()

            change_user_data[message.from_user.id] = {
                'channel_id': channel_id,
                'message_id': message.forward_from_message_id,  # Використовуємо правильний message_id
                'user_data': user_data,
                'content': {},
                'url_buttons': [],
                'pin': 0,
                'comments': 0
            }

            if message.text:
                content_info = message.text
                entities = message.entities 
                formatted_content = format_entities(content_info, entities)
                
                change_user_data[message.from_user.id]['text'] = formatted_content

            if message.photo:
                change_user_data[message.from_user.id]['content']['photo'] = message.photo[-1].file_id
                if message.caption:
                    print(message.caption)
                    content_info = message.caption
                    entities = message.caption_entities 
                    formatted_content =  format_entities(content_info, entities)
                    print(formatted_content)
                    change_user_data[message.from_user.id]['text'] = formatted_content

            if message.video:
                change_user_data[message.from_user.id]['content']['video'] = message.video.file_id
                if message.caption:
                    content_info = message.caption_entities 
                    entities = message.entities 
                    formatted_content =  format_entities(content_info, entities)
                    change_user_data[message.from_user.id]['text'] = formatted_content

            if message.document:
                change_user_data[message.from_user.id]['content']['document'] = message.document.file_id
                if message.caption:
                    content_info =  message.caption_entities 
                    entities = message.entities 
                    formatted_content =  format_entities(content_info, entities)
                    change_user_data[message.from_user.id]['text'] = formatted_content

            if message.animation:
                change_user_data[message.from_user.id]['content']['animation'] = message.animation.file_id
                if message.caption:
                    content_info = message.caption_entities 
                    entities = message.entities 
                    formatted_content =  format_entities(content_info, entities)
                    change_user_data[message.from_user.id]['text'] = formatted_content

            keyboard = InlineKeyboardMarkup(row_width=2)

            url_buttons = []  # Ініціалізація пустого списку для кнопок

            if message.reply_markup and isinstance(message.reply_markup, InlineKeyboardMarkup):
                existing_buttons = message.reply_markup.inline_keyboard
                change_user_data[message.from_user.id]['url_buttons'] = existing_buttons

                url_buttons = parse_existing_url_buttons(existing_buttons)

                change_user_data[user_id]['url_buttons'] = url_buttons

            # Створюємо нову клавіатуру з кнопками, якщо вони є
            new_keyboard = change_post(channel_id, change_user_data, message.from_user.id, url_buttons)
            for row in new_keyboard.inline_keyboard:
                keyboard.add(*row)

            await send_content_with_buttons(message, keyboard)
        else:
            await message.answer("Цей канал не зареєстрований у нашій базі даних.")
    else:
        await message.answer("Будь ласка, пересилайте пост саме з каналу.")
    
    print(change_user_data)
    await state.finish()



async def send_content_with_buttons(message: types.Message, keyboard: InlineKeyboardMarkup):
    """Відправляє медіа з описом та кнопками, якщо медіа є."""
    content = change_user_data[message.from_user.id]['content']
    
    caption = change_user_data[message.from_user.id]['text']

    if 'photo' in content:
        await bot.send_photo(message.chat.id, content['photo'], caption=caption,  parse_mode='HTML', reply_markup=keyboard)
    elif 'video' in content:
        await bot.send_video(message.chat.id, content['video'], caption=caption, parse_mode='HTML', reply_markup=keyboard)
    elif 'document' in content:
        await bot.send_document(message.chat.id, content['document'], caption=caption, parse_mode='HTML', reply_markup=keyboard)
    elif 'audio' in content:
        await bot.send_audio(message.chat.id, content['audio'], caption=caption, parse_mode='HTML', reply_markup=keyboard)
    elif 'voice' in content:
        await bot.send_voice(message.chat.id, content['voice'], caption=caption, parse_mode='HTML', reply_markup=keyboard)
    elif 'sticker' in content:
        await bot.send_sticker(message.chat.id, content['sticker'], parse_mode='HTML', reply_markup=keyboard)
    elif 'animation' in content:
        await bot.send_animation(message.chat.id, content['animation'], parse_mode='HTML', reply_markup=keyboard)
    else:
        await message.answer(caption, parse_mode='HTML', reply_markup=keyboard)

    return content.get('text', '') 


@dp.callback_query_handler(Text(startswith='change_add_'))
async def handle_description(callback_query: types.CallbackQuery, state: FSMContext):
    await EditPostState.waiting_for_new_text.set()
    await callback_query.message.answer(
        "Будь ласка, надішліть опис, який ви хочете додати або змінити:",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Назад", callback_data="back_to_my_post")
        )
    )


@dp.message_handler(state=EditPostState.waiting_for_new_text, content_types=['text'])
async def handle_description_content(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channel_id = change_user_data[user_id]['channel_id']
    content_info = message.text

    entities = message.entities 
    formatted_content =  format_entities(content_info, entities)
    change_user_data[message.from_user.id]['text'] = formatted_content

    url_buttons = change_user_data[user_id]['url_buttons']

    await send_content_with_buttons(message, change_post(channel_id, change_user_data, user_id, url_buttons))

    await state.finish()



@dp.callback_query_handler(Text(startswith='change_url_buttons_'))
async def handle_url_buttons(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[-1]

    change_user_data[user_id]['channel_id'] = channel_id
    
    await EditPostState.waiting_for_new_buttons.set()
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


@dp.message_handler(state=EditPostState.waiting_for_new_buttons, content_types=['text'])
async def handle_url_buttons_content(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    channel_id = change_user_data[user_id]['channel_id']
    content_info = change_user_data[user_id]['content'].get('text', '')

    url_buttons_text = message.text
    url_buttons = parse_url_buttons(url_buttons_text)

    change_user_data[user_id]['url_buttons'] = url_buttons
    await send_content_with_buttons(message, change_post(channel_id, change_user_data, user_id, url_buttons))

    await state.finish()



@dp.callback_query_handler(Text(startswith='change_pin_'))
async def handle_pin(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = change_user_data[user_id]['channel_id']
    url_buttons = change_user_data[user_id]['url_buttons']
    change_user_data[user_id]['pin'] = 1 if change_user_data[user_id]['pin'] == 0 else 0
    await callback_query.message.edit_reply_markup(reply_markup=change_post(channel_id, change_user_data, user_id, url_buttons))


@dp.callback_query_handler(Text(equals='change_save'))
async def handle_save(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    await callback_query.message.answer(
        "Ви впевнені, що хочете зберегти всі зміни?",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Так", callback_data="confirm_save"),
            InlineKeyboardButton("Ні", callback_data="cancel_save")
        )
    )

async def check_bot_permissions(channel_id, bot):
    member = await bot.get_chat_member(chat_id=channel_id, user_id=bot.id)
    if member.status not in ['administrator', 'creator']:
        raise Exception("Bot is not an administrator in this channel.")
    if not member.can_edit_messages:
        raise Exception("Bot does not have permission to edit messages.")


@dp.callback_query_handler(Text(equals='confirm_save'))
async def confirm_save(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    channel_id = change_user_data[user_id]['channel_id']
    content = change_user_data[user_id]['content']
    url_buttons = change_user_data[user_id]['url_buttons']

    new_text =change_user_data[user_id]['text']
    message_id = change_user_data[user_id]['message_id']
    pin = change_user_data[user_id]['pin']

    reply_markup = InlineKeyboardMarkup(row_width=2)
    if url_buttons:
        for row in url_buttons:
            reply_markup.row(*[InlineKeyboardButton(button_text, url=button_url) for button_text, button_url in row])

    try:
        await check_bot_permissions(channel_id, bot)
        if 'photo' in content:
            await bot.edit_message_caption(chat_id=channel_id, message_id=message_id, caption=new_text, parse_mode='HTML', reply_markup=reply_markup)
        elif 'video' in content:
            await bot.edit_message_caption(chat_id=channel_id, message_id=message_id, caption=new_text,parse_mode='HTML', reply_markup=reply_markup)
        elif 'document' in content:
            await bot.edit_message_caption(chat_id=channel_id, message_id=message_id, caption=new_text,parse_mode='HTML', reply_markup=reply_markup)
        elif 'audio' in content:
            await bot.edit_message_caption(chat_id=channel_id, message_id=message_id, caption=new_text,parse_mode='HTML', reply_markup=reply_markup)
        else:
            await bot.edit_message_text(chat_id=channel_id, message_id=message_id, text=new_text,parse_mode='HTML', reply_markup=reply_markup)

        if pin == 1:
            await bot.pin_chat_message(chat_id=channel_id, message_id=message_id)

        await callback_query.answer("Зміни успішно збережено!", show_alert=True)
        await callback_query.message.delete()
        await state.finish()
    except Exception as e:
        await callback_query.answer(f"Неможливо знайти повідомлення для редагування {message_id}.")
        
        await callback_query.message.answer(f"Повідомлення не знайдено або неможливо його змінити {message_id}.")
        
        print(e)

@dp.callback_query_handler(Text(equals='cancel_save'))
async def cancel_save(callback_query: types.CallbackQuery):
    await callback_query.answer("Збереження скасовано.", show_alert=True)
    await callback_query.message.delete()

@dp.callback_query_handler(text="change_media_")
async def process_channel_info(callback_query: types.CallbackQuery):
    await callback_query.answer("❌ Помилка а телегам API. Ви не можете редагувати медіа в пості.", show_alert=True)


def register_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(handle_forwarded_post, lambda c: c.data == 'add_channel')