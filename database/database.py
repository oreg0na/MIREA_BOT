import sqlite3
from config.config import *

db_file_user = path_db_users

def create_connection(db_file_user):
    conn = None
    try:
        conn = sqlite3.connect(db_file_user)
    except sqlite3.Error as e:
        print(e)
    return conn

def add_user(user_id):
    conn = create_connection(db_file_user)
    with conn:
        sql = ''' INSERT INTO users(user_id) VALUES(?) ON CONFLICT(user_id) DO NOTHING; '''
        cur = conn.cursor()
        cur.execute(sql, (user_id,))
        conn.commit()

def create_users_table():
    conn = create_connection(db_file_user)
    if conn is not None:
        create_table_sql = """CREATE TABLE IF NOT EXISTS users (
                                  keyboard_sent INTEGER DEFAULT 0,
                                  id integer PRIMARY KEY,
                                  user_id integer NOT NULL UNIQUE,
                                  keyboard_sent INTEGER DEFAULT 0
                              );"""
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
        except sqlite3.Error as e:
            print(e)
        finally:
            conn.close()
    else:
        print("Ошибка! Не удалось создать подключение к базе данных.")

def get_all_users():
    conn = create_connection(db_file_user)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users")
        user_ids = cur.fetchall()
        return [user_id[0] for user_id in user_ids]
def set_keyboard_sent(user_id, sent_status):
    conn = create_connection(db_file_user)
    with conn:
        sql = 'UPDATE users SET keyboard_sent = ? WHERE user_id = ?;'
        cur = conn.cursor()
        cur.execute(sql, (sent_status, user_id,))
        conn.commit()

def is_keyboard_sent(user_id):
    conn = create_connection(db_file_user)
    with conn:
        sql = 'SELECT keyboard_sent FROM users WHERE user_id = ?;'
        cur = conn.cursor()
        cur.execute(sql, (user_id,))
        result = cur.fetchone()
        if result:
            return result[0] == 1
        else:
            add_user(user_id)
            return False