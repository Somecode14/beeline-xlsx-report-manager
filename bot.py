import os
import logging
from datetime import datetime

import telebot

import xlsx
import config

if os.getenv("BOT_TOKEN") is not None:
    bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))
else:
    logging.exception(f"\n\nUnable to connect to the bot.\nFirst time using the program? Register a new bot via @BotFather on Telegram, then copy the API token into a .env file, like this:\nBOT_TOKEN=12345:ABCDE\n\nRestart the script after you are done.")
    exit(3)

context_descriptions = "/upload_records: Это служебная записка, добавить её в общую базу.\n/upload_stats: Это файл статистики, перезаписать его на этот.\n\n/cancel: Отмена, ничего не делать с этим файлом"

def show_help(message):
    bot.reply_to(message, "Добро пожаловать!\n\n/upload_records — добавить служебную записку в базу\n/upload_stats — перезаписать файл статистики\n/count_stats — провести анализ статистики\n/get_records — скачать базу данных служебных записок\n\nИли просто отправьте файл .xlsx, чтобы начать.")

@bot.message_handler(commands=['start'])
def start(message):
    if config.has_access(message):
        log_interaction(message, "sent /start")
        show_help(message)

@bot.message_handler(content_types=['document'])
def doc_no_context(message):
    if config.has_access(message):
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
        bot.reply_to(message, "Эта записка будет добавлена в базу после уточнения нескольких значений:\n\n✍️ Введите СЗ_Number.\n\n/cancel — отмена")
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
    if config.has_access(message):
        bot.reply_to(message, "Добавляем данные из служебной записки в базу данных.\n📄 Отправьте служебную записку в формате .xlsx.\n\n/cancel — отмена")
        log_interaction(message, "sent /upload_records. Awaiting for an .xslx file.")
        bot.register_next_step_handler(message, doc_upload_records)

@bot.message_handler(commands=['upload_stats'])
def upload_stats(message):
    if config.has_access(message):
        bot.reply_to(message, "Записываем новый файл статистики. Раннее загруженный файл статистики будет перезаписан!\n📄 Отправьте файл статистики в формате .xlsx.\n\n/cancel — отмена")
        log_interaction(message, "sent /upload_stats. Awaiting for an .xslx file.")
        bot.register_next_step_handler(message, doc_upload_stats, None)

# ===
# upload_records ↓
# ===

def doc_upload_records(message):
    if message.text is not None and message.text.startswith("/"):
        bot.reply_to(message, "Окей, загрузка служебной записки отменена.\nВведите команду заново.")
        log_interaction(message, "cancelled the upload.")
    else:
        try:
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
        except AttributeError:
            logging.info(f"Expected a file from {get_log_username(message.from_user)}, but got AttributeError.")
            bot.reply_to(message, "❌ Отправьте служебную записку в формате .xlsx — её можно прикрепить как документ или переслать из другого чата.\n\n/cancel, если хотите сделать что-то другое")
            bot.register_next_step_handler(message, doc_upload_records)

def sz_number_listener(message, xlsx_doc, path):
    if message.text is not None and message.text.startswith("/"):
        cancel(message)
    else:
        sz_number = message.text
        logging.info(f"СЗ_Number: {sz_number} (received from {get_log_username(message.from_user)})")
        bot.reply_to(message, "✍️ Введите CustomStatus (on/off).\n\n/cancel — отмена")
        bot.register_next_step_handler(message, custom_status_listener, xlsx_doc, path, sz_number)

def custom_status_listener(message, xlsx_doc, path, sz_number):
    if message.text is not None and message.text.startswith("/"):
        cancel(message)
    else:
        custom_status = message.text
        logging.info(f"CustomStatus: {custom_status} (received from {get_log_username(message.from_user)})")
        bot.reply_to(message, "✍️ Введите Филиал.\n\n/cancel — отмена")
        bot.register_next_step_handler(message, department_listener, xlsx_doc, path, sz_number, custom_status)

def department_listener(message, xlsx_doc, path, sz_number, custom_status):
    if message.text is not None and message.text.startswith("/"):
        cancel(message)
    else:
        department = message.text
        logging.info(f"Филиал: {department} (received from {get_log_username(message.from_user)})")
        bot.reply_to(message, "✍️ Введите StartTime.\n\n/cancel — отмена")
        bot.register_next_step_handler(message, start_time_listener, xlsx_doc, path, sz_number, custom_status, department)

def start_time_listener(message, xlsx_doc, path, sz_number, custom_status, department):
    if message.text is not None and message.text.startswith("/"):
        cancel(message)
    else:
        start_time = message.text
        logging.info(f"StartTime: {start_time} (received from {get_log_username(message.from_user)})")
        if custom_status == "on":
            end_time = ""
            logging.info(f"Leaving EndTime empty because CustomStatus is {custom_status}.")
            with open(path, "wb") as new_file:
                new_file.write(xlsx_doc)
            xlsx.get_worksheet(path, message, sz_number, custom_status, department, start_time, end_time)  # -> xlsx.py
        else:
            bot.reply_to(message, "✍️ Введите EndTime.\n\n/cancel — отмена")
            bot.register_next_step_handler(message, end_time_listener, xlsx_doc, path, sz_number, custom_status, department, start_time)

def end_time_listener(message, xlsx_doc, path, sz_number, custom_status, department, start_time):
    if message.text is not None and message.text.startswith("/"):
        cancel(message)
    else:
        end_time = message.text
        logging.info(f"EndTime: {end_time} (received from {get_log_username(message.from_user)})")
        with open(path, "wb") as new_file:
            new_file.write(xlsx_doc)
        xlsx.get_worksheet(path, message, sz_number, custom_status, department, start_time, end_time)  # -> xlsx.py

# ===
# upload_stats ↓
# ===

def doc_upload_stats(message, xlsx_doc):
    if xlsx_doc is None:
        if message.text is not None and message.text.startswith("/"):
            bot.reply_to(message, "Окей, загрузка статистики отменена.\nВведите команду заново.")
            log_interaction(message, "cancelled the upload.")
        else:
            try:
                doc_name = message.document.file_name
                log_interaction(message, f"sent a document: \"{doc_name}\"")
                if doc_name.endswith(".xlsx"):
                    xlsx_doc_info = bot.get_file(message.document.file_id)
                    xlsx_doc = bot.download_file(xlsx_doc_info.file_path)

                    with open("database/stats.xlsx", "wb") as new_file:
                        new_file.write(xlsx_doc)
                    bot.reply_to(message, "Файл статистики перезаписан.\n\n/count_stats, чтобы сгенерировать сводную таблицу")
                    logging.info("Overwrote database/stats.xlsx with the provided file.")
                else:
                    bot.reply_to(message, "К сожалению, поддерживаются только файлы формата .xlsx.")
                    logging.info("It is not an .xlsx file, nothing happened.")
            except AttributeError:
                logging.info(f"Expected a file from {get_log_username(message.from_user)}, but got AttributeError.")
                bot.reply_to(message, "❌ Отправьте файл статистики в формате .xlsx — его можно прикрепить как документ или переслать из другого чата.\n\n/cancel, если хотите сделать что-то другое")
                bot.register_next_step_handler(message, doc_upload_stats, None)
    else:
        with open("database/stats.xlsx", "wb") as new_file:
            new_file.write(xlsx_doc)
        bot.reply_to(message, "Файл статистики успешно перезаписан.\n\n/count_stats, чтобы сгенерировать сводную таблицу")
        logging.info(f"Overwrote database/stats.xlsx with the file provided by {get_log_username(message.from_user)}.")

# ===
# count_stats ↓
# ===

@bot.message_handler(commands=['count_stats'])
def count_stats(message):
    if config.has_access(message):
        bot.reply_to(message, "Провожу анализ статистики...")
        log_interaction(message, "sent /count_stats")
        xlsx.analyze_stats(message)

# ===
# get_records ↓
# ===

@bot.message_handler(commands=['get_records'])
def get_records(message):
    if config.has_access(message):
        try:
            log_interaction(message, "sent /get_records")
            database = open("database/database.xlsx", "rb")
            bot.send_document(message.chat.id, database, caption=f"База данных на {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", reply_to_message_id=message.message_id)
        except Exception as e:
            bot.reply_to(message, f"❌ Произошла ошибка при попытке получить базу данных.\n\n{e}")
            logging.exception(e)

# ===
# ADMIN
# ===

@bot.message_handler(commands=['whitelist_add'])
def whitelist_add(message):
    if message.from_user.id in config.admins:
        bot.reply_to(message, f"🔐 Добавляем пользователя в белый список. Он получит доступ к полной базе служебных записок, в том числе сможет загружать новые служебные записки, перезаписывать и генерировать статистику.\n\nВставьте внутренний ID пользователя — попросите его написать что-нибудь этому боту, чтобы получить его.\n\n/cancel — отмена")
        log_interaction(message, "sent /whitelist_add. Requesting User ID.")
        bot.register_next_step_handler(message, whitelist_modify_id, True)
    else:
        bot.reply_to(message, f"🔒 Отказано в доступе — команда доступна только администраторам.\nЕсли Вы считаете, что это ошибка, попросите системного администратора добавить ID {message.from_user.id} в список Администраторов в файле конфигурации.")


@bot.message_handler(commands=['whitelist_remove'])
def whitelist_remove(message):
    if message.from_user.id in config.admins:
        bot.reply_to(message, f"🔐 Удаляем пользователя из белого списка. Он больше не будет иметь доступа к полной базе служебных записок и статистике.\n\nЕсли пользователь является Администратором, как и Вы, он сможет снова добавить себя в whitelist. Чтобы удалить пользователя из списка администраторов, попросите системного администратора изменить файл конфигурации и перезапустить программу.\n\nВставьте внутренний ID пользователя — его можно найти в логах программы. Или попросите пользователя ввести /get_chat_id в ЛС с этим ботом и отправить Вам полученный ID.\n\n/cancel — отмена")
        log_interaction(message, "sent /whitelist_remove. Requesting User ID.")
        bot.register_next_step_handler(message, whitelist_modify_id, False)
    else:
        bot.reply_to(message, f"🔒 Отказано в доступе — команда доступна только администраторам.\nОбратитесь к одному из них или, если считаете, что это ошибка, попросите системного администратора добавить ID {message.from_user.id} в список Администраторов в файле конфигурации.")

def whitelist_modify_id(message, to_add: bool):
    if message.text.startswith("/"):
        bot.reply_to(message, "Отменено. Введите новую команду.")
        log_interaction(message, "sent some command. Cancelling adding to whitelist.")
    else:
        if message.from_user.id in config.admins:
            if message.text.isdecimal():
                if to_add:
                    if int(message.text) in config.whitelisted_users or message.text in config.whitelisted_users:
                        if int(message.text) in config.admins or message.text in config.admins:
                            bot.reply_to(message, f"❌ Пользователь с ID {message.text} уже в whitelistе. Ничего не изменилось.\n\nОн также является Администратором, то есть может изменять whitelist, как и Вы.\nЕсли хотите изменить это, отредактируйте файл конфигурации и перезапустите программу.")
                        else:
                            bot.reply_to(message, f"❌ Пользователь с ID {message.text} уже в whitelistе. Ничего не изменилось.\n\nЕсли Вы хотите выдать права Администратора этому пользователю, чтобы он тоже мог изменять whitelist, отредактируйте файл конфигурации и перезапустите программу. В целях безопасности через бота это сделать нельзя.")
                        log_interaction(message, f"tried to add ID {message.text} to whitelist. That user is already whitelisted; nothing changed.")
                    else:
                        config.whitelisted_users.add(int(message.text))
                        log_interaction(message, f"added ID {message.text} to whitelist.")
                        config.write_config()
                        bot.reply_to(message, f"🔓 Добавлен пользователь с ID {message.text} в whitelist. Теперь он может взаимодействовать с ботом, в том числе загружать и получать служебные записки и перезаписывать статистику.")
                else:
                    removed_successfully = False
                    if int(message.text) in config.whitelisted_users:
                        config.whitelisted_users.remove(int(message.text))
                        logging.info(f"Removed ID {message.text} (int) from whitelist.")
                        removed_successfully = True
                    if message.text in config.whitelisted_users:
                        config.whitelisted_users.remove(message.text)
                        logging.info(f"Removed ID {message.text} (string) from whitelist.")
                        removed_successfully = True
                    if removed_successfully:
                        config.write_config()
                        if int(message.text) in config.admins or message.text in config.admins:
                            bot.reply_to(message, f"🔓 Удалён пользователь с ID {message.text} из whitelistа.\n\n⚠️ ВНИМАНИЕ: Этот человек является Администратором. Он может вновь добавить себя в whitelist самостоятельно. Чтобы удалить пользователя из списка Администраторов, найдите его ID в файле конфигурации и удалите его оттуда. После этого обязательно перезапустите программу.\n\nСнять или выдать права Администратора нельзя через бота в целях безопасности.")
                        else:
                            bot.reply_to(message, f"🔓 Удалён пользователь с ID {message.text} из whitelistа. Теперь он не может взаимодействовать с ботом.")
                    else:
                        bot.reply_to(message, f"❌ Пользователя с ID {message.text} нет в whitelistе. Ничего не изменилось.")
                        log_interaction(message, f"tried to remove ID {message.text} from the whitelist. That user was not whitelisted in the first place; nothing changed.")
            else:
                bot.reply_to(message, "Подойдёт только внутренний ID — он должен состоять только из цифр.\nПопросите пользователя написать /get_chat_id в ЛС с ботом и сообщить полученный внутренний ID Вам. Внутренний ID также можно найти в логах — он отображается при любом взаимодействии пользователя с ботом.\n\nВведите внутренний ID пользователя.\n\n/cancel — отмена")
                bot.register_next_step_handler(message, whitelist_modify_id, to_add)


@bot.message_handler(commands=['get_chat_id'])
def get_chat_id(message):
    bot.reply_to(message, f"Current Chat ID: {message.chat.id}")
    log_interaction(message, "sent /get_chat_id")
# ===
#
# ===

@bot.message_handler()
def msg(message):
    if config.has_access(message):
        show_help(message)
        log_message(message)

def log_interaction(message, text):
    logging.info(f"<{get_log_username(message.from_user)}> {text}")
    if config.extended_logs_in_chats:
        for chat in config.chats:
            try:
                bot.send_message(chat, f"<{get_log_username(message.from_user)}> {text}")
            except telebot.apihelper.ApiTelegramException:
                logging.warning(f"Chat {chat} not found. Use /get_chat_id and copy the ID into config.py")

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