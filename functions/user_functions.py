from main import bot
import mistune, re, asyncio, datetime, pytz, os, ast
from database.user_db import fetch_posts_for_mailing, get_channel_name_by_id, get_channel_link_by_id, delete_post_from_db, mark_post_as_posted
from aiogram.types import InputFile
from keyboards.user_keyboards import post_shedule_keyboard


def format_entities(text, entities):
    formatted_text = text
    shift = 0  # Щоб компенсувати зміщення через додані теги

    for entity in entities:
        entity_type = entity['type']
        offset = entity['offset']
        length = entity['length']  # Вже обчислена довжина кожного сегмента тексту

        # Витягуємо текст, який відповідає цій сутності
        entity_text = text[offset:offset + length]

        # В залежності від типу сутності, обгортаємо текст відповідним тегом
        if entity_type == 'bold':
            formatted_text = (
                formatted_text[:offset + shift] +
                f"<b>{entity_text}</b>" +
                formatted_text[offset + length + shift:]
            )
            shift += 7  # Додаємо зміщення для тегів <b>...</b> (7 символів)
        elif entity_type == 'italic':
            formatted_text = (
                formatted_text[:offset + shift] +
                f"<i>{entity_text}</i>" +
                formatted_text[offset + length + shift:]
            )
            shift += 7  # Зміщення для тегів <i>...</i>
            
        elif entity_type == 'pre':
            formatted_text = (
                formatted_text[:offset + shift] +
                f"<code>{entity_text}</code>" +
                formatted_text[offset + length + shift:]
            )
        elif entity_type == 'code':  # Додано підтримку для коду
            formatted_text = (
                formatted_text[:offset + shift] +
                f"<code>{entity_text}</code>" +
                formatted_text[offset + length + shift:]
            )
            shift += 13  # Зміщення для тегів <code>...</code>
        elif entity_type == 'strikethrough':
            formatted_text = (
                formatted_text[:offset + shift] +
                f"<s>{entity_text}</s>" +
                formatted_text[offset + length + shift:]
            )
            shift += 7  # Зміщення для тегів <s>...</s>
        elif entity_type == 'underline':
            formatted_text = (
                formatted_text[:offset + shift] +
                f"<u>{entity_text}</u>" +
                formatted_text[offset + length + shift:]
            )
            shift += 7  # Зміщення для тегів <u>...</u>
        elif entity_type == 'blockquote':
            formatted_text = (
                formatted_text[:offset + shift] +
                f"<blockquote>{entity_text}</blockquote>" +
                formatted_text[offset + length + shift:]
            )
            shift += 25  # Зміщення для тегів <blockquote>...</blockquote>

    return formatted_text


async def download_media(file_id, file_path):
    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, file_path)

def parse_url_buttons(text):
    buttons = []
    lines = text.split('\n')
    for line in lines:
        if ' | ' in line:
            parts = line.split(' | ')
            row = []
            for part in parts:
                button_parts = part.split(' - ')
                if len(button_parts) == 2:
                    button_text = button_parts[0].strip()
                    button_url = button_parts[1].strip()
                    row.append((button_text, button_url))
            buttons.append(row)
        else:
            button_parts = line.split(' - ')
            if len(button_parts) == 2:
                button_text = button_parts[0].strip()
                button_url = button_parts[1].strip()
                buttons.append([(button_text, button_url)])
    return buttons

def parse_existing_url_buttons(existing_buttons):
    buttons = []
    for row in existing_buttons:
        button_row = []
        for button in row:
            button_text = button.text
            button_url = button.url
            button_row.append((button_text, button_url))
        buttons.append(button_row)
    return buttons




def parse_db_buttons(db_buttons):
    buttons = []
    for row in db_buttons:
        # Assuming row is a list of tuples
        button_row = [(button[0], button[1]) for button in row]  # Extract text and URL
        buttons.append(button_row)
    return buttons





async def send_mailing():
    tz = pytz.timezone('Europe/Kyiv')
    now = datetime.datetime.now(tz)

    current_date = now.strftime('%Y-%m-%d')  # Формат у вигляді 'yyyy-mm-dd'
    current_hour = now.strftime('%H')          # Формат години
    current_minute_tens = now.minute  # Десятки хвилин
    
    print(current_minute_tens)

    posts = fetch_posts_for_mailing(current_date, current_hour, current_minute_tens)

    if posts:
        await send_posts(posts)  # Виклик функції для надсилання постів
    else:
        print("NO POSTS")

async def send_posts(posts):
    # Логіка для надсилання постів
    for post in posts:
        post_id = post[0]
        user_id = post[1]
        channel_id = post[2]
        content = post[3]
        media_type = post[4]
        media_path = post[5]
        url_buttons = post[6]
        bell = post[7]
        pin = post[8]
        scheduled_time = post[9]

        # Перетворення bell в булевий тип
        disable_notification = True if bell == 0 else False

        try:
            url_buttons = ast.literal_eval(url_buttons) if url_buttons else []
        except (ValueError, SyntaxError) as e:
            print(f"Error unpacking url_buttons: {e}")
            url_buttons = []

        channel_name = get_channel_name_by_id(channel_id)
        link = get_channel_link_by_id(channel_id)

        # Надсилаємо контент на канал
        if media_path:
            if media_type == 'photo':
                if media_path.startswith('posts'):
                    media = InputFile(media_path)
                    message = await bot.send_photo(
                        channel_id,
                        media,
                        caption=content,
                        parse_mode="HTML",
                        reply_markup=post_shedule_keyboard(channel_id, user_data=None, user_id=user_id, url_buttons=url_buttons),
                        disable_notification=disable_notification
                    )
                else:
                    message = await bot.send_photo(
                        channel_id,
                        media_path,
                        caption=content,
                        parse_mode="HTML",
                        reply_markup=post_shedule_keyboard(channel_id, user_data=None, user_id=user_id, url_buttons=url_buttons),
                        disable_notification=disable_notification
                    )
            elif media_type == 'video':
                if media_path.startswith('posts'):
                    media = InputFile(media_path)
                    message = await bot.send_video(
                        channel_id,
                        media,
                        caption=content,
                        parse_mode="HTML",
                        reply_markup=post_shedule_keyboard(channel_id, user_data=None, user_id=user_id, url_buttons=url_buttons),
                        disable_notification=disable_notification
                    )
                else:
                    message = await bot.send_document(
                        channel_id,
                        media_path,
                        caption=content,
                        parse_mode="HTML",
                        reply_markup=post_shedule_keyboard(channel_id, user_data=None, user_id=user_id, url_buttons=url_buttons),
                        disable_notification=disable_notification
                    )
            elif media_type == 'document':
                if media_path.startswith('posts'):
                    media = InputFile(media_path)
                    message = await bot.send_document(
                        channel_id,
                        media,
                        caption=content,
                        parse_mode="HTML",
                        reply_markup=post_shedule_keyboard(channel_id, user_data=None, user_id=user_id, url_buttons=url_buttons),
                        disable_notification=disable_notification
                    )
                else:
                    message = await bot.send_message(
                        channel_id,
                        content,
                        parse_mode="HTML",
                        reply_markup=post_shedule_keyboard(channel_id, user_data=None, user_id=user_id, url_buttons=url_buttons),
                        disable_notification=disable_notification
                    )
        else:
            message = await bot.send_message(
                channel_id,
                content,
                parse_mode="HTML",
                reply_markup=post_shedule_keyboard(channel_id, user_data=None, user_id=user_id, url_buttons=url_buttons),
                disable_notification=disable_notification
            )
        # Видалити медіа файл після відправки
        # if media_path and media_path.startswith('posts'):
        #     try:
        #         os.remove(media_path)
        #         print(f"File {media_path} deleted successfully.")
        #     except Exception as e:
        #         print(f"Error deleting file {media_path}: {e}")
        if pin:
            await bot.pin_chat_message(channel_id, message.message_id)
        user_message = f"<b>Пост успішно опубліковано на каналі</b> <a href='{link}'>{channel_name}</a> "
        # delete_post_from_db(user_id, post_id)
        mark_post_as_posted(post_id)
        await bot.send_message(user_id, user_message, parse_mode="HTML")
    
    