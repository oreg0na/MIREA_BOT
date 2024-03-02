import telebot
from telebot import types
import docx2txt
import os

os.chdir("/Users/vicedant/Desktop/MIREA_BOT/") 

import pandas as pd

bot = telebot.TeleBot("Token")

# Декоратор для логирования команд
def log_command(func):
    def wrapper(message):
        user_id = message.from_user.id
        command = message.text
        print(f"Получена команда: {command} от пользователя с ID: {user_id}")
        func(message)
    return wrapper

@bot.message_handler(commands=['start']) 
@log_command
def start_message(message):
    bot.send_message(
        message.chat.id,  
        "Добро пожаловать, дорогие студенты группы ЭФБО-07-23! Я бот, созданный чтобы облегчить ваше взаимодействие и учебу. Вы можете использовать следующие команды: \n\n /group - получить список группы"
    )

@bot.message_handler(commands=['group'])
@log_command
def send_docx_message(message):
    user_id = message.from_user.id
    doc_path = "resources/group_list.docx"
    with open(doc_path, 'rb') as doc:
        bot.send_document(message.chat.id, doc, caption="Вот список всей группы:")

print("Бот запущен и готов к работе. Ожидание команд...")
bot.polling()