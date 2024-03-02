# Бот для группы ЭФБО-07-23 (ИПТИП)

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![SQLite](https://img.shields.io/badge/sqlite-gray?style=for-the-badge&logo=sqlite)
![TeleBot](https://img.shields.io/badge/telebot-rad?style=for-the-badge&logo=telebot)

## Installation
```
https://github.com/oreg0na/MIREA_BOT.git
cd MIREA_BOT
pip install telebot, sqlite3
```

## Directories
`config` — API токен бота, путь создание db, admin id (все передаваемые данные)

`database` - база данных всех пользователей с момента создания таблицы бд, которые воспользовались ботом (для того, чтобы админ мог кидать важные новости всем пользователям бота)

`resources` - хранит в себе файл .docx (список всех учеников, используется в команде /group)

`wrapper` - логирует любые вводы команд пользователями (отображает их в консоль запуска и выводит ID,тег и введенную команду)

### Ваши идеи
[![Telegram](https://img.shields.io/badge/Telegram-blue?style=for-the-badge&logo=Telegram)](https://t.me/svpg16)
