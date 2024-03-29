import telebot
import json
import subprocess
from datetime import datetime
import time
import random
import requests
from requests.exceptions import ReadTimeout

from wrapper.log import log_command
from database.database import create_users_table, add_user, get_all_users
from database.crypto import conn, cursor, encrypt, decrypt
from config.config import *
from keyboard.key import *
from parse.parsing import get_ip_info
from ssh.sshconnect import ssh_connect, ssh_close, ssh_cmd, get_user_state, set_user_state

def load_birthdays():
    with open(path_token, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data['date_group']

bot = telebot.TeleBot(token)
ssh_client = None
user_step = {}
max_attempts, attempt = 36, 0

while attempt < max_attempts:
    try:
        response = requests.get(f'https://api.telegram.org/bot{token}/getUpdates', timeout=30)
        print(response.json())
        break
    except ReadTimeout:
        print(f"Запрос превысил время ожидания. Попытка {attempt+1} из {max_attempts}. Повторная попытка через 5 минут.")
        attempt += 1
        if attempt < max_attempts:
            time.sleep(300)
        else:
            print("Достигнуто максимальное количество попыток. Пожалуйста, попробуйте позже.")

def get_user_step(user_id):
    if user_id in user_step:
        return user_step[user_id]
    else:
        user_step[user_id] = 0
        return 0

def process_range_step(message):
    try:
        user_step[message.chat.id] = 0
        range_numbers = message.text.split()
        if len(range_numbers) != 2:
            raise ValueError
        min_num, max_num = int(range_numbers[0]), int(range_numbers[1])
        if min_num >= max_num:
            raise ValueError
        random_number = random.randint(min_num, max_num)
        bot.reply_to(message, f"🆙 Случайное число: {random_number}")
    except ValueError:
        msg = bot.reply_to(message, "❗️ Пожалуйста введи корректный диапозон чисел (например '1 10')")
        bot.register_next_step_handler(msg, process_range_step)

def check_and_send_birthday_messages():
    today = datetime.now().strftime("%d.%m")
    print(today)
    birthdays_today = [person for person in load_birthdays() if person['birthdate'][:5] == today]
    
    for person in birthdays_today:
        message = f"🎆 Сегодня {today}, день рождение у {person['name']}."
        bot.send_message(admin, message)
        print('сообщение о днях рождениях отправлено')

@bot.message_handler(commands=['addpassword'])
def add_password(message):
    try:
        parts = message.text.split(maxsplit=4)
        if len(parts) != 4:
            raise ValueError("Неверное количество аргументов.")
        _, url, login, password = parts
        # Проверяем, начинается ли URL с http:// или https://
        if not (url.startswith('http://') or url.startswith('https://')):
            raise ValueError("URL должен начинаться с http:// или https://")
        chat_id = message.chat.id
        url_encrypted = encrypt(url)
        login_encrypted = encrypt(login)
        password_encrypted = encrypt(password)
        cursor.execute("INSERT INTO passwords (chat_id, url, login, password_encrypted) VALUES (?, ?, ?, ?)", 
                       (chat_id, url_encrypted, login_encrypted, password_encrypted))
        conn.commit()
        bot.reply_to(message, "Пароль успешно сохранен.\nДля просмотра всех сохранённых паролей: /listpasswords")
    except ValueError as e:
        bot.reply_to(message, f"Ошибка. {str(e)} Используйте формат: /addpassword [ссылка] [логин/почта/телефон] [пароль]")


@bot.message_handler(commands=['listpassword'])
def list_passwords(message):
    chat_id = message.chat.id
    cursor.execute("SELECT url, login, password_encrypted FROM passwords WHERE chat_id=?", (chat_id,))
    passwords = cursor.fetchall()
    if passwords:
        response = "Ваши сохраненные данные:\n" + "\n".join([f"Ссылка: {decrypt(url)}, Логин: {decrypt(login)}, Пароль: {decrypt(password_encrypted)}" for url, login, password_encrypted in passwords])
    else:
        response = "Сохраненных паролей нет.\nЧтобы добавить пароль используйте: /addpassword"
    bot.reply_to(message, response)

@bot.message_handler(commands=['delpassword'])
def delete_password(message):
    try:
        _, url_to_delete = message.text.split(maxsplit=1)
        chat_id = message.chat.id
        cursor.execute("SELECT rowid, url FROM passwords WHERE chat_id=?", (chat_id,))
        rows = cursor.fetchall()

        for row in rows:
            rowid, encrypted_url = row
            if decrypt(encrypted_url) == url_to_delete:
                cursor.execute("DELETE FROM passwords WHERE rowid=?", (rowid,))
                conn.commit()
                bot.reply_to(message, "Пароль успешно удален.\nДля просмотра всех сохраненных пароль: /listpassword")
                return
        bot.reply_to(message, "Пароль не найден.")
    except ValueError:
        bot.reply_to(message, "Ошибка. Используйте формат: /delpassword [ссылка]")

markup_inline = types.InlineKeyboardMarkup(row_width=2)
markup_inline.add(btn_ping, btn_addpswd, btn_random)

@bot.message_handler(commands=['start']) 
@log_command
def start_message(message):
    add_user(message.from_user.id)
    user_id = message.chat.id
    bot.send_message(
        user_id,  
        "📌 Добро пожаловать, дорогие студенты института ИПТИП(МИРЭА)! Я бот, созданный чтобы облегчить ваше взаимодействие и учебу. Вы можете использовать следующие команды:",
        reply_markup=markup_inline
    )

@bot.message_handler(commands=['random'])
def random_command(message):
    user_id = message.chat.id
    msg = bot.send_message(user_id, "➡️ Введи диапазон чисел через пробел (например '1 10'): ")
    user_step[message.chat.id] = 1
    bot.register_next_step_handler(msg, process_range_step)

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

@bot.message_handler(commands=['ping'])
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

@bot.message_handler(commands=['ssh-connect'])
def ssh_connect_start(message):
    msg = bot.reply_to(message, "💣 Введите данные SSH в формате: host port username password")
    bot.register_next_step_handler(msg, process_ssh_connect)
    set_user_state(message.from_user.id, 'ssh_connected')

def process_ssh_connect(message):
    try:
        details = message.text.split()
        if len(details) != 4:
            raise ValueError("Invalid format")
        success, response = ssh_connect(*details)
        bot.send_message(message.chat.id, response)
    except Exception as e:
        bot.reply_to(message, '⛔️ Не удалось подключиться. Error: {}'.format(str(e)))

@bot.message_handler(commands=['ssh-close'])
def handle_ssh_close(message):
    response = ssh_close(message.from_user.id)
    bot.reply_to(message, response)

@bot.message_handler(commands=['ssh-cmd'])
def handle_ssh_cmd_start(message):
    if get_user_state(message.from_user.id) != 'ssh_connected':
        bot.reply_to(message, "📎 Нет активного SSH-соединения. Используйте /ssh-connect для запуска нового сеанса.")
        return
    msg = bot.reply_to(message, "> Введите команду для выполнения:")
    bot.register_next_step_handler(msg, process_ssh_cmd)

def process_ssh_cmd(message):
    command = message.text
    response = ssh_cmd(command)
    bot.send_message(message.chat.id, response)

def process_ssh_connect(message):
    try:
        details = message.text.split()
        if len(details) != 4:
            raise ValueError("Invalid format")
        host, port, username, password = details
        if port != '22':
            bot.reply_to(message, "⚠️ Поддерживается только порт 22. Пожалуйста, попробуйте снова.")
            return
        success, response = ssh_connect(host, port, username, password)
        bot.send_message(message.chat.id, response)
    except Exception as e:
        bot.reply_to(message, '⛔️ Не удалось подключиться. Error: {}'.format(str(e)))

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'addpassword':
        bot.send_message(callback.message.chat.id, 'Используйте формат: /addpassword [ссылка] [логин/почта/телефон] [пароль]')
    if callback.data == 'ping':
        ping(callback.message)
    if callback.data == 'random':
        random_command(callback.message)

print("Бот запущен и готов к работе. Ожидание команд...")
create_users_table()
check_and_send_birthday_messages()
bot.polling(none_stop=True)