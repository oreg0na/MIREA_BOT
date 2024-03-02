def log_command(func):
    def wrapper(message):
        user_id = message.from_user.id
        username = message.from_user.username
        command = message.text
        user_info = f"{user_id}, @{username}" if username else f"{user_id}"
        print(f"Получена команда: {command} от пользователя с ID и ником: {user_info}")
        func(message)
    return wrapper