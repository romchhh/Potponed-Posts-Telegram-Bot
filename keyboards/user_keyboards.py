from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta

def get_start_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.row(KeyboardButton("Створити пост"), KeyboardButton("Редагувати пост"))
    keyboard.row(KeyboardButton("Контент план"), KeyboardButton("Налаштування"))
    keyboard.row(KeyboardButton("Шаблони"))
    
    return keyboard


def get_cancel_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_button = KeyboardButton(text="← Відмінити")
    keyboard.add(cancel_button)
    return keyboard

def get_back_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    back_button = InlineKeyboardButton("← Назад", callback_data="back_to_posts")
    keyboard.add(back_button)
    return keyboard

def back_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    back_button = InlineKeyboardButton("← Назад", callback_data="back_to_my_post")
    keyboard.add(back_button)
    return keyboard


def create_post(channel_id, user_data, user_id, url_buttons=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    if url_buttons:
        for row in url_buttons:
            keyboard.row(*[InlineKeyboardButton(button_text, url=button_url) for button_text, button_url in row])

    keyboard.add(
        InlineKeyboardButton("Медіа", callback_data=f"media_{channel_id}"),
        InlineKeyboardButton("Додати опис", callback_data=f"add_{channel_id}"),
        InlineKeyboardButton("🔔" if user_data.get(user_id, {}).get('bell', 0) == 1 else "🔕", callback_data=f"bell_{channel_id}"),
        InlineKeyboardButton("URL-кнопки", callback_data=f"url_buttons_{channel_id}"),
    )
    # keyboard.add(
    #     InlineKeyboardButton("Приховане повідомлення", callback_data=f"hidden_continue_{channel_id}"),
    # )
    keyboard.add(
        InlineKeyboardButton("✅ Коментарі" if user_data.get(user_id, {}).get('comments', 0) == 1 else "☑️ Коментарі", callback_data=f"comments_{channel_id}"),
        InlineKeyboardButton("✅ Закріпити" if user_data.get(user_id, {}).get('pin', 0) == 1 else "☑️ Закріпити", callback_data=f"pin_{channel_id}"),
        InlineKeyboardButton("← Відміна", callback_data=f"back_to"),
        InlineKeyboardButton("Далі →", callback_data=f"next_{channel_id}")
    )

    return keyboard


def change_shedule_post(channel_id, user_data, user_id, post_id, url_buttons=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    if url_buttons:
        for row in url_buttons:
            keyboard.row(*[InlineKeyboardButton(button_text, url=button_url) for button_text, button_url in row])

    keyboard.add(
        InlineKeyboardButton("Медіа", callback_data=f"shedulemedia_{channel_id}"),
        InlineKeyboardButton("Додати опис", callback_data=f"sheduleadd_{channel_id}"),
        InlineKeyboardButton("🔔" if user_data.get(user_id, {}).get('bell', 0) == 1 else "🔕", callback_data=f"shedulebell_{channel_id}"),
        InlineKeyboardButton("URL-кнопки", callback_data=f"sheduleurl_buttons_{channel_id}"),
    )
    # keyboard.add(
    #     InlineKeyboardButton("Приховане повідомлення", callback_data=f"hidden_continue_{channel_id}"),
    # )
    keyboard.add(
        InlineKeyboardButton("✅ Коментарі" if user_data.get(user_id, {}).get('comments', 0) == 1 else "☑️ Коментарі", callback_data=f"shedulecomments_{channel_id}"),
        InlineKeyboardButton("✅ Закріпити" if user_data.get(user_id, {}).get('pin', 0) == 1 else "☑️ Закріпити", callback_data=f"shedulepin_{channel_id}"),
        InlineKeyboardButton("🗑 Видалити пост", callback_data=f"delete_shedule_post_{post_id}_{channel_id}"),
        InlineKeyboardButton("✏️ Зберегти зміни", callback_data=f"shedulepost_save_{post_id}_{channel_id}"),
    )
    
    keyboard.add(
        InlineKeyboardButton("← Назад", callback_data=f"back_to"),
        InlineKeyboardButton("Далі →", callback_data=f"shedulenext_{channel_id}"),
    )
    
    return keyboard


def publish_post(channel_id, user_data, user_id):
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton("Таймер видалення: ні" if user_data.get(user_id, {}).get('deletetimer', 0) == 1 else "Таймер видалення: так", callback_data=f"deletetimer_{channel_id}"),
 
    )
    keyboard.add(
        InlineKeyboardButton("✅ Це рекламний пост" if user_data.get(user_id, {}).get('addpost', 0) == 1 else "☑️ Це рекламний пост", callback_data=f"addpost_{channel_id}"),
    )
    keyboard.add(
        InlineKeyboardButton("🕰 Відкласти", callback_data=f"timer_{channel_id}"),
        InlineKeyboardButton("💈 Опублікувати", callback_data=f"publish_{channel_id}"),
        InlineKeyboardButton("← Назад", callback_data=f"back_to")
    )

    return keyboard



def publish_shedule_post(channel_id, user_data, user_id):
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton("Таймер видалення: ні" if user_data.get(user_id, {}).get('deletetimer', 0) == 1 else "Таймер видалення: так", callback_data=f"sheduledeletetimer_{channel_id}"),
 
    )
    keyboard.add(
        InlineKeyboardButton("✅ Це рекламний пост" if user_data.get(user_id, {}).get('addpost', 0) == 1 else "☑️ Це рекламний пост", callback_data=f"sheduleaddpost_{channel_id}"),
    )
    keyboard.add(
        InlineKeyboardButton("🕰 Відкласти", callback_data=f"sheduletimer_{channel_id}"),
        InlineKeyboardButton("💈 Опублікувати", callback_data=f"shedulepublish_{channel_id}"),
        InlineKeyboardButton("← Назад", callback_data=f"back_to")
    )

    return keyboard

def post_shedule_keyboard(channel_id, user_data, user_id, url_buttons=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    if url_buttons:
        for row in url_buttons:
            keyboard.row(*[InlineKeyboardButton(button_text, url=button_url) for button_text, button_url in row])
    return keyboard


def post_keyboard(channel_id, user_data, user_id, url_buttons=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    if url_buttons:
        for row in url_buttons:
            keyboard.row(*[InlineKeyboardButton(button_text, url=button_url) for button_text, button_url in row])
    return keyboard


def change_post(channel_id, change_user_data, user_id, url_buttons=None):
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard = InlineKeyboardMarkup(row_width=2)
    if url_buttons:
        for row in url_buttons:
            keyboard.row(*[InlineKeyboardButton(button_text, url=button_url) for button_text, button_url in row])
    keyboard.add(
        InlineKeyboardButton("Медіа", callback_data=f"change_media_"),
        InlineKeyboardButton("Додати опис", callback_data=f"change_add_{channel_id}"),
        InlineKeyboardButton("URL-кнопки", callback_data=f"change_url_buttons_{channel_id}"),
        InlineKeyboardButton("✅ Закріпити" if change_user_data[user_id].get('pin', 0) == 1 else "☑️ Закріпити", callback_data=f"change_pin_{channel_id}"),
        InlineKeyboardButton("✏️ Зберегти", callback_data=f"change_save"),
        InlineKeyboardButton("← Відміна", callback_data=f"back_to"),
    )

    return keyboard


def generate_calendar(current_date: datetime, scheduled_dates: set) -> InlineKeyboardMarkup:
    today = current_date.date()
    days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
    week_buttons = [InlineKeyboardButton(text=day, callback_data=f"day_{day}") for day in days_of_week]

    date_buttons = []
    start_date = today + timedelta(days=-2)
    end_date = today + timedelta(days=12)

    start_of_week = start_date - timedelta(days=start_date.weekday())

    dates = [start_of_week + timedelta(days=i) for i in range((end_date - start_of_week).days + 1)]

    for date in dates:
        if start_date <= date <= end_date:
            if date in scheduled_dates:
                date_button = InlineKeyboardButton(text=f"{date.strftime('%d')}🔹", callback_data=f"date_{date.strftime('%Y-%m-%d')}")
            elif date == today:
                date_button = InlineKeyboardButton(text=f"{date.strftime('%d')}🔸", callback_data=f"date_{date.strftime('%Y-%m-%d')}")
            else:
                date_button = InlineKeyboardButton(text=date.strftime("%d"), callback_data=f"date_{date.strftime('%Y-%m-%d')}")
        else:
            date_button = InlineKeyboardButton(text=" ", callback_data="empty")

        date_buttons.append(date_button)

    while len(date_buttons) % 7 != 0:
        date_buttons.append(InlineKeyboardButton(text=" ", callback_data="empty"))

    calendar_buttons = InlineKeyboardMarkup(row_width=7)
    calendar_buttons.add(*week_buttons)
    calendar_buttons.add(*date_buttons)
    calendar_buttons.add(InlineKeyboardButton(text="Всі відкладені пости", callback_data="all_scheduled"))

    return calendar_buttons




def template_post(channel_id, user_data, user_id, url_buttons=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    if url_buttons:
        for row in url_buttons:
            keyboard.row(*[InlineKeyboardButton(button_text, url=button_url) for button_text, button_url in row])

    keyboard.add(
        InlineKeyboardButton("Медіа", callback_data=f"templatemedia_{channel_id}"),
        InlineKeyboardButton("Додати опис", callback_data=f"templateadd_{channel_id}"),
        InlineKeyboardButton("URL-кнопки", callback_data=f"templateurl_buttons_{channel_id}"),
    )
    keyboard.add(
        InlineKeyboardButton("← Відміна", callback_data=f"back_to"),
        InlineKeyboardButton("Готово →", callback_data=f"save_template_{channel_id}")
    )

    return keyboard






def change_template_post(channel_id, user_data, user_id, post_id, url_buttons=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    if url_buttons:
        for row in url_buttons:
            keyboard.row(*[InlineKeyboardButton(button_text, url=button_url) for button_text, button_url in row])

    keyboard.add(
        InlineKeyboardButton("Опублікувати", callback_data=f"publishtemplate_{post_id}"),
    )
    keyboard.add(
        InlineKeyboardButton("🗑 Видалити пост", callback_data=f"delete_template_post_{post_id}_{channel_id}"),
    )
    keyboard.add(
        InlineKeyboardButton("← Назад", callback_data=f"back_to"),
    )
    
    return keyboard




def publish_template(channel_id, template_data, user_id, url_buttons=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    if url_buttons:
        for row in url_buttons:
            keyboard.row(*[InlineKeyboardButton(button_text, url=button_url) for button_text, button_url in row])

    keyboard.add(
        InlineKeyboardButton("Медіа", callback_data=f"publishtemplatemedia_{channel_id}"),
        InlineKeyboardButton("Додати опис", callback_data=f"publishtemplateadd_{channel_id}"),
        InlineKeyboardButton("🔔" if template_data.get(user_id, {}).get('bell', 0) == 1 else "🔕", callback_data=f"templatebell_{channel_id}"),
        InlineKeyboardButton("URL-кнопки", callback_data=f"publishtemplateurl_buttons_{channel_id}"),
    )
    # keyboard.add(
    #     InlineKeyboardButton("Приховане повідомлення", callback_data=f"hidden_continue_{channel_id}"),
    # )
    keyboard.add(
        InlineKeyboardButton("✅ Коментарі" if template_data.get(user_id, {}).get('comments', 0) == 1 else "☑️ Коментарі", callback_data=f"templatecomments_{channel_id}"),
        InlineKeyboardButton("✅ Закріпити" if template_data.get(user_id, {}).get('pin', 0) == 1 else "☑️ Закріпити", callback_data=f"templatepin_{channel_id}"),
    )
    
    keyboard.add(
        InlineKeyboardButton("← Назад", callback_data=f"back_to"),
        InlineKeyboardButton("Далі →", callback_data=f"templatenext_{channel_id}"),
    )
    
    return keyboard


def publish_template_post(channel_id, template_data, user_id):
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton("Таймер видалення: ні" if template_data.get(user_id, {}).get('deletetimer', 0) == 1 else "Таймер видалення: так", callback_data=f"templatedeletetimer_{channel_id}"),
    )
    keyboard.add(
        InlineKeyboardButton("✅ Це рекламний пост" if template_data.get(user_id, {}).get('addpost', 0) == 1 else "☑️ Це рекламний пост", callback_data=f"templateaddpost_{channel_id}"),
    )
    keyboard.add(
        InlineKeyboardButton("💈 Опублікувати", callback_data=f"templatepublish_{channel_id}"),
        InlineKeyboardButton("← Назад", callback_data=f"back_to")
    )

    return keyboard