import json
import logging

import bot

# CONFIG

read_database_on_each_input = False
# Reloads the database file on each .xlsx document sent by users.
# `False` is recommended unless the file is modified externally.
#
# `False` — loads the database file only when the script starts, then keeps the data in RAM, writing the file every time it gets modified.
# `True` — reloads the database file after each user input.

#
# ⚠️ DO NOT MODIFY THE CODE BELOW — use config.json. It is generated on first startup.
#

def write_config():
    try:
        with open("config.json", "w", encoding="utf-8") as config_file:
            json.dump({"send_logs_to_chats": list(chats), "send_extended_logs": extended_logs_in_chats, "whitelisted_users": list(whitelisted_users), "admin_users": list(admins)}, config_file,
                      ensure_ascii=False, indent=4)
            logging.info("Saved config to config.json.")
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        logging.exception("Failed to save config to config.json.")

try:
    with open("config.json", "r", encoding="utf-8") as config_file:
        config_json = json.load(config_file)

        chats = set(config_json.get("send_logs_to_chats", []))
        # List of chats the bot should send notifications to. DMs are also supported.
        # The bot sends a message when anyone uploads a Records file via any chat or DM.
        # Add the bot to a chat, then use /get_chat_id and copy the ID into the config file. Include negative signs if present.

        extended_logs_in_chats = config_json.get("send_extended_logs", False)
        # Also log all bot interactions to chats listed above, including simple commands like /start
        # `False` by default

        whitelisted_users = set(config_json.get("whitelisted_users", []))
        logging.info(f"{len(whitelisted_users)} whitelisted users.")

        admins = set(config_json.get("admin_users", []))
        logging.info(f"{len(admins)} admin users.")

except (FileNotFoundError, json.decoder.JSONDecodeError):
        chats = set()
        extended_logs_in_chats = False
        whitelisted_users = set()
        admins = set()
        with open("config.json", "w", encoding="utf-8") as file:
            write_config()
        logging.info("Created a new config.json file. Please check it or restart the program with default settings.")
        exit(0)

def has_access(message):
    user_id = message.from_user.id
    if user_id in whitelisted_users or str(user_id) in whitelisted_users:
        return True
    else:
        bot.bot.reply_to(message, f"🔒 Отказано в доступе.\nПопросите системного администратора добавить ID {user_id} в whitelist.")
        bot.log_interaction(message, "— Access denied.")
        return False