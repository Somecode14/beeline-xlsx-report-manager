import os
import logging
from datetime import datetime

import telebot

import xlsx

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))

context_descriptions = "/upload_records: Это служебная записка, добавить её в общую базу.\n/upload_stats: Это файл статистики, перезаписать его на этот.\n\n/cancel: Отмена, ничего не делать с этим файлом"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Добро пожаловать!\n\n/upload_records — добавить служебную записку в базу\n/upload_stats — перезаписать файл статистики\n/count_stats — провести анализ статистики\n/get_records — скачать базу данных служебных записок\n\nИли просто отправьте файл .xlsx, чтобы начать.")
    log_interaction(message, "sent /start")

@bot.message_handler(content_types=['document'])
def doc_no_context(message):
    # Runs when the user sends a document without running any commands before that.
    # The bot asks whether the document is a list of records or a stats file.
    doc_name = message.document.file_name
    log_interaction(message, f"sent a document: \"{doc_name}\"")
    if doc_name.endswith(".xlsx"):
        xlsx_doc_info = bot.get_file(message.document.file_id)
        xlsx_doc = bot.download_file(xlsx_doc_info.file_path)
        path = "input/" + doc_name

        bot.reply_to(message, f"Файл получен. Что нужно сделать?\n\n{context_descriptions}")
        bot.register_next_step_handler(message, get_context, xlsx_doc, path)
    else:
        bot.reply_to(message, "К сожалению, принимаются только файлы формата .xlsx.")
        logging.info("It is not an .xlsx file, nothing happened.")

def get_context(message, xlsx_doc, path):
    # Runs when the user sends a document without running any commands before that
    # and only then answers whether the document is a list of records or a stats file.
    if message.text == "/upload_records":
        bot.reply_to(message, "Эта записка будет добавлена в базу после уточнения нескольких значений:\n\n✍️ Введите СЗ_Number.")
        bot.register_next_step_handler(message, sz_number_listener, xlsx_doc, path)
    elif message.text == "/upload_stats":
        doc_upload_stats(message, xlsx_doc)
    elif message.text == "/cancel":
        bot.reply_to(message, "Окей, загрузка отменена.\nОтпавьте файл заново или введите /start для подробносткей.")
        log_interaction(message, "cancelled uploading.")
    else:
        bot.reply_to(message, f"Не понял. Пожалуйста, выберите команду из списка, кликнув или коснувшись её.\n\nЧто это за файл?\n\n{context_descriptions}")
        bot.register_next_step_handler(message, get_context, xlsx_doc, path)

# Commands without any documents previously sent ↓

@bot.message_handler(commands=['upload_records'])
def upload_records(message):
    bot.reply_to(message, "Добавляем данные из служебной записки в базу данных.\n📄 Отправьте служебную записку в формате .xlsx.")
    log_interaction(message, "sent /upload_records. Awaiting for an .xslx file.")
    bot.register_next_step_handler(message, doc_upload_records)

@bot.message_handler(commands=['upload_stats'])
def upload_stats(message):
    bot.reply_to(message, "Записываем новый файл статистики. Раннее загруженный файл статистики будет перезаписан!\n📄 Отправьте файл статистики в формате .xlsx.")
    log_interaction(message, "sent /upload_stats. Awaiting for an .xslx file.")
    bot.register_next_step_handler(message, doc_upload_stats, None)

# ===
# upload_records ↓
# ===

def doc_upload_records(message):
    doc_name = message.document.file_name
    log_interaction(message, f"sent a document: \"{doc_name}\"")
    if doc_name.endswith(".xlsx"):
        xlsx_doc_info = bot.get_file(message.document.file_id)
        xlsx_doc = bot.download_file(xlsx_doc_info.file_path)
        path = "input/" + doc_name

        # СЗ_Number

        # Request the number via Telegram bot
        bot.reply_to(message, "✍️ Введите СЗ_Number.\n\n/cancel — отмена")
        bot.register_next_step_handler(message, sz_number_listener, xlsx_doc, path)
    else:
        bot.reply_to(message, "К сожалению, поддерживаются только файлы формата .xlsx.")
        logging.info("It is not an .xlsx file, nothing happened.")

def sz_number_listener(message, xlsx_doc, path):
    if message.text.startswith("/"):
        cancel(message)
    else:
        sz_number = message.text
        logging.info(f"СЗ_Number: {sz_number} (received from {get_log_username(message.from_user)})")
        bot.reply_to(message, "✍️ Введите CustomStatus (on/off).\n\n/cancel — отмена")
        bot.register_next_step_handler(message, custom_status_listener, xlsx_doc, path, sz_number)

def custom_status_listener(message, xlsx_doc, path, sz_number):
    if message.text.startswith("/"):
        cancel(message)
    else:
        custom_status = message.text
        logging.info(f"CustomStatus: {custom_status} (received from {get_log_username(message.from_user)})")
        bot.reply_to(message, "✍️ Введите StartTime.\n\n/cancel — отмена")
        bot.register_next_step_handler(message, start_time_listener, xlsx_doc, path, sz_number, custom_status)

def start_time_listener(message, xlsx_doc, path, sz_number, custom_status):
    if message.text.startswith("/"):
        cancel(message)
    else:
        start_time = message.text
        logging.info(f"StartTime: {start_time} (received from {get_log_username(message.from_user)})")
        bot.reply_to(message, "✍️ Введите EndTime.\n\n/cancel — отмена")
        bot.register_next_step_handler(message, end_time_listener, xlsx_doc, path, sz_number, custom_status, start_time)

def end_time_listener(message, xlsx_doc, path, sz_number, custom_status, start_time):
    if message.text.startswith("/"):
        cancel(message)
    else:
        end_time = message.text
        logging.info(f"EndTime: {end_time} (received from {get_log_username(message.from_user)})")
        with open(path, "wb") as new_file:
            new_file.write(xlsx_doc)
        xlsx.get_worksheet(path, message, sz_number, custom_status, start_time, end_time)  # -> xlsx.py

# ===
# upload_stats ↓
# ===

def doc_upload_stats(message, xlsx_doc):
    if xlsx_doc is None:
        doc_name = message.document.file_name
        log_interaction(message, f"sent a document: \"{doc_name}\"")
        if doc_name.endswith(".xlsx"):
            xlsx_doc_info = bot.get_file(message.document.file_id)
            xlsx_doc = bot.download_file(xlsx_doc_info.file_path)

            with open("database/stats.xlsx", "wb") as new_file:
                new_file.write(xlsx_doc)
            bot.reply_to(message, "Файл статистики перезаписан.")
            logging.info("Overwrote database/stats.xlsx with the provided file.")
        else:
            bot.reply_to(message, "К сожалению, поддерживаются только файлы формата .xlsx.")
            logging.info("It is not an .xlsx file, nothing happened.")
    else:
        with open("database/stats.xlsx", "wb") as new_file:
            new_file.write(xlsx_doc)
        bot.reply_to(message, "Файл статистики успешно перезаписан.")
        logging.info(f"Overwrote database/stats.xlsx with the file provided by {get_log_username(message.from_user)}.")

# ===
# count_stats ↓
# ===

@bot.message_handler(commands=['count_stats'])
def count_stats(message):
    bot.reply_to(message, "Провожу анализ статистики...")
    log_interaction(message, "sent /count_stats")
    xlsx.analyze_stats(message)

# ===
# get_records ↓
# ===

@bot.message_handler(commands=['get_records'])
def get_records(message):
    log_interaction(message, "sent /get_records")
    database = open("database/database.xlsx", "rb")
    bot.send_document(message.chat.id, database, caption=f"База данных на {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", reply_to_message_id=message.message_id)
    xlsx.analyze_stats(message)

# ===
#
# ===

@bot.message_handler()
def msg(message):
    bot.reply_to(message, "Введите /start, чтобы начать, или отправьте файл .xlsx для загрузки новых данных.")
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

def cancel(message):
    log_interaction(message, "sent some command. Interrupting current flow.")
    bot.reply_to(message, "Загрузка отменена. Пожалуйста, введите команду заново, чтобы её выполнить.")

bot.infinity_polling()