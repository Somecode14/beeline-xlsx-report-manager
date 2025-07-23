import logging
from pathlib import Path
from dotenv import load_dotenv

# Enables logging.
logging.basicConfig(format='[%(asctime)s %(name)s %(levelname)s]: %(message)s', level=logging.INFO)

# Creates necessary directories
Path("input").mkdir(parents=True, exist_ok=True)
Path("database").mkdir(parents=True, exist_ok=True)
Path("output").mkdir(parents=True, exist_ok=True)

# IMPORTANT: you have to create a .env file in the project directory for the bot to work.
# Filename: `.env`
# Contents ↓
# BOT_TOKEN=12345:ABCDE
# ↑ (where 12345:ABCDE is your Bot API Token, provided by @BotFather on Telegram)
load_dotenv()

import bot