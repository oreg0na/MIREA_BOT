import telebot
from telebot import types
import mimetypes # С помощью MimeTypes определяем MIME тип для файла .docx
import docx2txt
import os

os.chdir("/Users/vicedant/Desktop/MIREA_BOT/") 

import pandas as pd
from io import BytesIO

bot = telebot.TeleBot("Token")

@bot.message_handler(commands=['start']) 
def start_message(message):
    bot.send_message(
        message.chat.id,  
        "Добро пожаловать, дорогие студенты группы ЭФБО-07-23! Я бот, созданный чтобы облегчить ваше взаимодействие и учебу. Вы можете использовать следующие команды: \n\n /group - получить список группы"
    )

@bot.message_handler(commands=['group'])
def send_group(message):
    text = docx2txt.process('resources/group_list.docx')
    # Парсим  
    data = []
    for line in text.split('\n'):
        splits = line.split(':')  
        if len(splits) == 2:
            name, group = splits
            data.append({"name": name, "group": group})     
    df = pd.DataFrame(data)
    with pd.ExcelWriter('output/group_list.xlsx') as writer: 
        df.to_excel(writer)
    writer.close()
    doc = open('output/group_list.xlsx', 'rb')
    bot.send_document(message.chat.id, doc)

bot.polling()