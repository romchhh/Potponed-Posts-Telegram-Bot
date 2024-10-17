import sqlite3
import datetime
from datetime import datetime, timedelta

current_time = datetime.now()

conn = sqlite3.connect('data/data.db')
cursor = conn.cursor()

def get_user_name_by_id(user_id):
    cursor.execute('SELECT user_name FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None
    
    
def get_user_id_by_name(user_name):
    cursor.execute('SELECT user_id FROM users WHERE user_name = ?', (user_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None
    
    
def add_admin_to_channel(channel_id, channel_name, user_id, link):
    try:
        with sqlite3.connect('data/data.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO channels (channel_id, channel_name, channel_admin, link) VALUES (?, ?, ?, ?)",
                (channel_id, channel_name, user_id, link)
            )
            conn.commit()
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
