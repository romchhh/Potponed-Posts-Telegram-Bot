import sqlite3
import datetime
from datetime import datetime, timedelta

current_time = datetime.now()

conn = sqlite3.connect('data/data.db')
cursor = conn.cursor()

def create_table():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            user_name TEXT,
            blocked BOOLEAN DEFAULT 0 CHECK(blocked IN (0, 1))
        )
    ''')
    conn.commit()



def add_user(user_id, user_name):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    existing_user = cursor.fetchone()
    if existing_user is None:
        cursor.execute('''
            INSERT INTO users (user_id, user_name)
            VALUES (?, ?)
        ''', (user_id, user_name))
        conn.commit()
    
def get_user_channels(user_id):
    cursor.execute("SELECT channel_id, channel_name FROM channels WHERE channel_admin = ?", (user_id,))
    return cursor.fetchall()

def is_channel_in_db(channel_id):
    cursor.execute("SELECT * FROM channels WHERE channel_id = ?", (channel_id,))
    return cursor.fetchone() is not None

def add_channel_to_db(channel_id, channel_name, channel_admin, link):
    if is_channel_in_db(channel_id):
        return False 
    cursor.execute("INSERT INTO channels (channel_id, channel_name, channel_admin, link) VALUES (?, ?, ?, ?)", (channel_id, channel_name, channel_admin, link))
    conn.commit()
    return True 


def get_channel_name_by_id(channel_id):
    cursor.execute('SELECT channel_name FROM channels WHERE channel_id = ?', (channel_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None
    
def get_channel_link_by_id(channel_id):
    cursor.execute('SELECT link FROM channels WHERE channel_id = ?', (channel_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

def save_post_to_db(user_id, channel_id, content, media_type, media_path, url_buttons, bell, pin, scheduled_time):
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            channel_id TEXT,
            content TEXT,
            media_type TEXT,
            media_path TEXT,
            url_buttons TEXT,
            bell INTEGER,
            pin INTEGER,
            scheduled_time TIMESTAMP
        )
    ''')
    cursor.execute(''' 
        INSERT INTO posts (user_id, channel_id, content, media_type, media_path, url_buttons, bell, pin, scheduled_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, channel_id, content, media_type, media_path, url_buttons, bell, pin, scheduled_time))
    conn.commit()


def update_post_in_db(post_id, user_id, channel_id, content, media_type, media_path, url_buttons, bell, pin):
    cursor.execute('''
        UPDATE posts
        SET user_id = ?, channel_id = ?, content = ?, media_type = ?, media_path = ?, url_buttons = ?, bell = ?, pin = ?
        WHERE id = ?
    ''', (user_id, channel_id, content, media_type, media_path, url_buttons, bell, pin, post_id))
    conn.commit()

def update_post_in_db_without_photo(post_id, user_id, channel_id, content, url_buttons, bell, pin):
    cursor.execute('''
        UPDATE posts
        SET user_id = ?, channel_id = ?, content = ?, url_buttons = ?, bell = ?, pin = ?
        WHERE id = ?
    ''', (user_id, channel_id, content, url_buttons, bell, pin, post_id))
    conn.commit()


def is_channel_in_db(channel_id):
    cursor.execute("SELECT * FROM channels WHERE channel_id = ?", (channel_id,))
    result = cursor.fetchone()
    return result is not None

def get_scheduled_times(user_id):
    cursor.execute('SELECT scheduled_time FROM posts WHERE user_id = ?', (user_id,))
    scheduled_times = cursor.fetchall()
    return {datetime.fromisoformat(row[0]).date() for row in scheduled_times}


def get_posts_for_date(user_id: int, selected_date: datetime.date):
    cursor.execute('''SELECT id, user_id, channel_id, content, media_type, media_path, url_buttons, bell, pin, scheduled_time FROM posts 
                      WHERE DATE(scheduled_time) = ?''',
                   (selected_date, ))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    posts = [dict(zip(column_names, row)) for row in rows]
    return posts

def get_sheduled_posts_for_date(user_id: int, selected_date):
    cursor.execute('''SELECT id, user_id, channel_id, content, media_type, media_path, url_buttons, bell, pin, scheduled_time FROM posts 
                      WHERE scheduled_time = ?''',
                   (selected_date,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    posts = [dict(zip(column_names, row)) for row in rows]
    return posts

def delete_post_from_db(user_id, post_id):
    media_path = None  # Initialize media_path
    try:
        cursor.execute("SELECT media_path FROM posts WHERE id = ?", (post_id,))
        row = cursor.fetchone()
        if row:
            media_path = row[0] 
        cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        conn.commit()
        return cursor.rowcount > 0, media_path  # Return whether deletion was successful and the media path
    except Exception as e:
        print(f"Error deleting post: {e}")
        return False, None  # Return failure status and None for media path



def get_scheduled_posts(user_id, channel_id):
    # Get the current date and time
    current_date = datetime.now()
    # Calculate the date and time for two days ago
    two_days_ago = current_date - timedelta(days=2)

    # Execute the query to retrieve posts
    cursor.execute(''' 
        SELECT channel_id, content, scheduled_time, posted
        FROM posts
        WHERE scheduled_time > ? AND channel_id = ?
        ORDER BY scheduled_time ASC
    ''', (two_days_ago, channel_id))

    posts = cursor.fetchall()
    return posts


def create_templates_db():
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            channel_id TEXT,
            content TEXT,
            media_type TEXT,
            media_path TEXT,
            url_buttons TEXT)
    ''')
    conn.commit()
    

def get_templates_for_channel(user_id, channel_id):
    cursor.execute('''SELECT * FROM templates WHERE user_id = ? AND channel_id = ?''', (user_id, channel_id))
    templates = cursor.fetchall()

    return templates

def get_template_by_id(template_id):
    cursor.execute('''SELECT * FROM templates WHERE id = ?''', (template_id,))
    template = cursor.fetchone()

    return template


def save_template_to_db(user_id, channel_id, content_info, media_type, media_path, url_buttons_str):
    cursor.execute(''' 
        INSERT INTO templates (user_id, channel_id, content, media_type, media_path, url_buttons)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, channel_id, content_info, media_type, media_path, url_buttons_str))
    conn.commit()
    
def delete_template_from_db(user_id, post_id):
    try:
        cursor.execute("DELETE FROM templates WHERE user_id = ? AND id = ?", (user_id, post_id))
        conn.commit()
        return cursor.rowcount > 0 
    except Exception as e:
        print(f"Error deleting post: {e}")
        return False
    
    
def fetch_posts_for_mailing(current_date, current_hour, current_minute_tens):
    current_minute_range_start = current_minute_tens - 14
    current_minute_range_end = current_minute_tens + 1
    cursor.execute('''
        SELECT * FROM posts WHERE 
        DATE(scheduled_time) = ? AND 
        strftime('%H', scheduled_time) = ? AND 
        CAST(strftime('%M', scheduled_time) AS INTEGER) >= ? AND 
        CAST(strftime('%M', scheduled_time) AS INTEGER) <= ?
    ''', (current_date, current_hour, current_minute_range_start, current_minute_range_end))
    
    print(current_minute_range_start, current_minute_range_end)
    
    print(current_minute_range_start, current_minute_range_end)
    
    posts = cursor.fetchall()
    return posts



def mark_post_as_posted(post_id):
    cursor.execute("UPDATE posts SET posted = ? WHERE id = ?", (1, post_id))
    conn.commit()
