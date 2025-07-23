
# CONFIG

read_database_on_each_input = False
# Reloads the database file on each .xlsx document sent by users.
# `False` is recommended unless the file is modified externally.
#
# `False` — loads the database file only when the script starts, then keeps the data in RAM, writing the file every time it gets modified.
# `True` — reloads the database file after each user input.

chats = {}
# List of chats the bot should send notifications to, separated with commas. DMs are also supported.
# The bot sends a message when anyone uploads a Records file via any chat or DM.
# Add the bot to a chat, then use /get_chat_id and copy the ID here. Include negative signs if present.

extended_logs_in_chats = False
# Also log all bot interactions to chats listed above, including simple commands like /start
# `False` by default