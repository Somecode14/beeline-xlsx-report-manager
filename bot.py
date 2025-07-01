import os
import logging

import telebot

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))

@bot.message_handler(commands=['start'])
def start(message):
    # TODO: добавить описание команды выгрузки статистики
    bot.reply_to(message, "Добро пожаловать! Отправьте файл .xlsx для добавления информации в базу.\nИли введите /start, чтобы показать это сообщение ещё раз.")
    log_interaction(message, "sent /start")

@bot.message_handler()
def msg(message):
    # TODO: добавить описание команды выгрузки статистики
    bot.reply_to(message, "Отправьте файл .xlsx для добавления информации в базу или введите /start, чтобы показать приветственное сообщение.")
    log_message(message)

def log_interaction(message, text):
    logging.info(f"<{get_log_username(message.from_user)}> {text}")

def log_message(message):
    logging.info(f"<{get_log_username(message.from_user)}>: {message.text}")

def get_log_username(user):
    # Форматирует имя пользователя и ID для использования в логах.
    # Если пользователь не имеет @юзернейма, отображаются Имя и Фамилия, указанные в профиле
    if user.username is None:
        if user.last_name is None:
            return f"{user.first_name} ({user.id})"
        else:
            return f"{user.first_name} {user.last_name} ({user.id})"
    else:
        return f"@{user.username} ({user.id})"


bot.infinity_polling()