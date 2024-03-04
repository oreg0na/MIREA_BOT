from config.config import path_key, path_db_passwords
from cryptography.fernet import Fernet
import sqlite3

def load_key():
    return open(path_key, 'rb').read()

key = load_key()
cipher_suite = Fernet(key)

conn = sqlite3.connect(path_db_passwords, check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS passwords
               (chat_id INTEGER, url TEXT, login TEXT, password_encrypted TEXT)''')
conn.commit()

def encrypt(text):
    return cipher_suite.encrypt(text.encode()).decode()

def decrypt(text):
    return cipher_suite.decrypt(text.encode()).decode()