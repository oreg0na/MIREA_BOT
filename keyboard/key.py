from telebot import types

btn_ping = types.InlineKeyboardButton("📍 Узнать свой пинг", callback_data='ping')
btn_addpswd = types.InlineKeyboardButton("🔐 Добавить пароль", callback_data='addpassword')
btn_random = types.InlineKeyboardButton("🔢 Рандомное число", callback_data='random')
