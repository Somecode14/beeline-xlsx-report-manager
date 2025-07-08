import os
import logging

import telebot

import xlsx

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))

@bot.message_handler(commands=['start'])
def start(message):
    # TODO: добавить описание команды выгрузки статистики
    bot.reply_to(message, "Добро пожаловать! Отправьте файл .xlsx для добавления информации в базу.\nИли введите /start, чтобы показать это сообщение ещё раз.")
    log_interaction(message, "sent /start")

@bot.message_handler(content_types=['document'])
def doc(message):
    doc_name = message.document.file_name
    log_interaction(message, f"sent a document: \"{doc_name}\"")
    if doc_name.endswith(".xlsx"):
        xlsx_doc_info = bot.get_file(message.document.file_id)
        xlsx_doc = bot.download_file(xlsx_doc_info.file_path)
        path = "input/" + doc_name

        # СЗ_Number

        # Request the number via Telegram bot
        bot.reply_to(message, "✍️ Введите СЗ_Number.")
        bot.register_next_step_handler(message, sz_number_listener, xlsx_doc, path)
    else:
        bot.reply_to(message, "К сожалению, поддерживаются только файлы формата .xlsx.")
        logging.info("It is not an .xlsx file, nothing happened.")

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

def sz_number_listener(message, xlsx_doc, path):
    sz_number = message.text
    logging.info(f"СЗ_Number: {sz_number} (received from {get_log_username(message.from_user)})")
    bot.reply_to(message, "✍️ Введите CustomStatus (on/off).")
    bot.register_next_step_handler(message, custom_status_listener, xlsx_doc, path, sz_number)

def custom_status_listener(message, xlsx_doc, path, sz_number):
    custom_status = message.text
    logging.info(f"CustomStatus: {custom_status} (received from {get_log_username(message.from_user)})")
    bot.reply_to(message, "✍️ Введите StartTime.")
    bot.register_next_step_handler(message, start_time_listener, xlsx_doc, path, sz_number, custom_status)

def start_time_listener(message, xlsx_doc, path, sz_number, custom_status):
    start_time = message.text
    logging.info(f"StartTime: {start_time} (received from {get_log_username(message.from_user)})")
    bot.reply_to(message, "✍️ Введите EndTime.")
    bot.register_next_step_handler(message, end_time_listener, xlsx_doc, path, sz_number, custom_status, start_time)

def end_time_listener(message, xlsx_doc, path, sz_number, custom_status, start_time):
    end_time = message.text
    logging.info(f"EndTime: {end_time} (received from {get_log_username(message.from_user)})")
    with open(path, "wb") as new_file:
        new_file.write(xlsx_doc)
    xlsx.get_worksheet(path, message, sz_number, custom_status, start_time, end_time)  # -> xlsx.py

bot.infinity_polling()