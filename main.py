import telebot
# import openpyxl
import docx2txt

import pandas as pd
from io import BytesIO

bot = telebot.TeleBot("6630080242:AAF2fHCKMtoJn6t8UJNgOU6hHtzxZ8LQv_U")

@bot.message_handler(commands=['start']) 
def start_message(message):
    bot.send_message(
        message.chat.id,  
        "Добро пожаловать, дорогие студенты группы ЭФБО-07-23! Я бот, созданный чтобы облегчить ваше взаимодействие и учебу. Вы можете использовать следующие команды: \n\n /group - получить список группы"
    )

@bot.message_handler(commands=['group'])
def group_list(message):
    doc_text = docx2txt.process("resources/group_list.docs")
    lines = doc_text.split("\n")
    data = []
    for line in lines:
        splits = line.split(":")
        if len(splits) == 2:
            name, group = splits 
            data.append({"name": name.strip(), "group": group.strip()})
    df = pd.DataFrame(data) 
    with BytesIO() as output:
        with pd.ExcelWriter(output) as writer:
            df.to_excel(writer)
        output.seek(0)
        bot.send_document(message.chat.id, output, filename="resources/group_list.docs") 

bot.polling()