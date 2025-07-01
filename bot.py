import os
import logging

import telebot

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Добро пожаловать! Отправьте файл .xlsx для добавления информации в базу.\nИли введите /start, чтобы показать это сообщение ещё раз.")
    log_interaction(message, "Sent /start")

@bot.message_handler()
def msg(message):
    bot.send_message(message.chat.id, message.text)
    log_message(message)

def log_interaction(message, text):
    logging.info(f"<{message.from_user.id}>: {text}")

def log_message(message):
    logging.info(f"<{message.from_user.id}>: {message.text}")

bot.infinity_polling()