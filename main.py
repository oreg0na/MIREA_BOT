import telebot
import openpyxl

from io import BytesIO

bot = telebot.TeleBot("TOKEN")

@bot.message_handler(commands=['start']) 
def start_message(message):
    bot.send_message(
        message.chat.id,  
        "Добро пожаловать, дорогие студенты группы ЭФБО-07-23! Я бот, созданный чтобы облегчить ваше взаимодействие и учебу. Вы можете использовать следующие команды: \n\n /group - получить список группы"
    )

@bot.message_handler(commands=['group'])
def send_group(message):
    wb = openpyxl.load_workbook('resources/group_list.xlsx') 
    sheet = wb.active
    with BytesIO() as output:
        wb.save(output)
        output.seek(0)
        bot.send_document(message.chat.id, output, filename='resources/group_list.xlsx')

bot.polling()