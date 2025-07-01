import os

import telebot

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hello")

bot.infinity_polling()