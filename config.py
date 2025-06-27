# config.py
import os
import json
from dotenv import load_dotenv

load_dotenv()

CONFIG_FILE = "config.json"
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
LOG_CHANNEL_ID = int(os.getenv("CHECKIN_LOG_CHANNEL_ID"))
YOUR_USER_ID = int(os.getenv("YOUR_USER_ID"))


def load_config():
    if not os.path.exists(CONFIG_FILE) or os.path.getsize(CONFIG_FILE) == 0:
        return {}
    with open(CONFIG_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)
