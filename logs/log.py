def log_command(func):
    def wrapper(message):
        user_id = message.from_user.id
        command = message.text
        print(f"Получена команда: {command} от пользователя с ID: {user_id}")
        func(message)
    return wrapper