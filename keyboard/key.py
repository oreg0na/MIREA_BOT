from telebot import types

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn_group = types.KeyboardButton("Список группы")
btn_ping = types.KeyboardButton("Узнать свой пинг")