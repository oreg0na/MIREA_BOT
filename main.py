import telebot
from telebot import types
import os
import sqlite3

from wrapper.log import log_command
from database.database import db_file, create_connection, create_users_table, add_user, get_all_users
from config.config import *

os.chdir(path_file) 
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start']) 
@log_command
def start_message(message):
    add_user(message.from_user.id)
    bot.send_message(
        message.chat.id,  
        "📌 Добро пожаловать, дорогие студенты группы ЭФБО-07-23! Я бот, созданный чтобы облегчить ваше взаимодействие и учебу. Вы можете использовать следующие команды: \n\n1️⃣/group - получить список группы"
    )

@bot.message_handler(commands=['group'])
@log_command
def send_docx_message(message):
    user_id = message.from_user.id
    doc_path = "resources/group_list.docx"
    with open(doc_path, 'rb') as doc:
        bot.send_document(message.chat.id, doc, caption="😁 Вот список всей группы:")

@bot.message_handler(commands=['send'])
def send_to_all(message):
    if message.from_user.id == admin:
        text_to_send = message.text.replace('/send ', '', 1)
        user_ids = get_all_users()
        for user_id in user_ids:
            try:
                bot.send_message(user_id, f"✏️ [Объявление] {text_to_send}")
            except Exception as e:
                print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
    else:
        bot.reply_to(message, "⛔️ У вас нет доступа к админ-командам")


print("Бот запущен и готов к работе. Ожидание команд...")
create_users_table()
bot.polling()