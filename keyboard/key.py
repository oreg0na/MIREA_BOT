from telebot import types

markup_inline = types.InlineKeyboardMarkup(row_width=2)
btn_group = types.InlineKeyboardButton("📃 Список группы", callback_data='group')
btn_ping = types.InlineKeyboardButton("📍 Узнать свой пинг", callback_data='ping')
btn_addpswd = types.InlineKeyboardButton("🔐 Добавить пароль", callback_data='addpassword')
