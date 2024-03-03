import telebot
import os
import time
import subprocess

from wrapper.log import log_command
from database.database import create_users_table, add_user, get_all_users
from config.config import *
from keyboard.key import *
from parse.parsing import get_ip_info

os.chdir(path_file) 
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start']) 
@log_command
def start_message(message):
    add_user(message.from_user.id)
    markup.add(btn_group, btn_ping)

    bot.send_message(
        message.chat.id,  
        "📌 Добро пожаловать, дорогие студенты группы ЭФБО-07-23! Я бот, созданный чтобы облегчить ваше взаимодействие и учебу. Вы можете использовать следующие команды:",
        reply_markup=markup
    )

@bot.message_handler(commands=['group'])
@log_command
def send_docx_message(message):
    user_id = message.from_user.id
    doc_path = "resources/group_list.docx"
    with open(doc_path, 'rb') as doc:
        bot.send_document(message.chat.id, doc, caption="😁 Вот список всей группы:")
    pass
# кнопки
@bot.message_handler(func=lambda message: message.text == "Список группы")
def handle_group_button(message):
    sent_message = bot.send_message(message.chat.id, "Вызываю команду /group...")
    time.sleep(1)
    bot.delete_message(message.chat.id, sent_message.message_id)
    send_docx_message(message)

@bot.message_handler(func=lambda message: message.text == "Узнать свой пинг")
def handle_ping_button(message):
    sent_message = bot.send_message(message.chat.id, "Вызываю команду /ping...")
    time.sleep(1)
    bot.delete_message(message.chat.id, sent_message.message_id)
    ping(message)
#
@bot.message_handler(commands=['send'])
@log_command
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

@bot.message_handler(commands=['ping'])
@log_command
def ping(message):
    bot.send_message(message.chat.id, "🔗 Введите IP-адрес, на который нужно выполнить ping:")
    bot.register_next_step_handler(message, process_ping)

def process_ping(message):
    ip_address = message.text
    try:
        output = subprocess.check_output(['ping', '-c', '3', ip_address])
        ip_info = get_ip_info(ip_address)
        response_text = f"⚡️ Пинг до {ip_address}:\n\n{output.decode('utf-8')}\n\n"
        response_text += f"📍 Информация об IP-адресе:\nСтрана: {ip_info.get('country', 'неизвестно')}\nГород: {ip_info.get('city', 'неизвестно')}"
        bot.send_message(message.chat.id, response_text)
    except Exception as e:
        bot.send_message(message.chat.id, f"😔 Ошибка при выполнении ping, скорее всего вы указали некорректный IP-адрес")


print("Бот запущен и готов к работе. Ожидание команд...")
create_users_table()
bot.polling(none_stop=True)