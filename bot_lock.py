from drive_utils import download_file, upload_file, authenticate_drive
import socket
import json
from utils import get_now
from discord.ext import tasks
from config import FOLDER_ID

service = authenticate_drive()


async def register_lock():
    hostname = socket.gethostname()
    now = get_now().isoformat()

    lock_data = {"active_hostname": hostname, "started_at": now}

    # Save to local file
    with open("bot.lock", "w") as f:
        json.dump(lock_data, f)

    # Upload to Drive
    upload_file(service, "bot.lock", folder_id=FOLDER_ID)
    print(f"🔐 Bot {hostname} đã ghi quyền kiểm soát vào bot.lock")


bot_lock = None


async def start_bot_lock(bot):
    global bot_lock

    @tasks.loop(seconds=30)
    async def check_lock():
        hostname = socket.gethostname()

        try:
            download_file(service, "bot.lock", folder_id=FOLDER_ID)
            with open("bot.lock", "r") as f:
                data = json.load(f)
                if data["active_hostname"] != hostname:
                    print(
                        f"⛔ Mất quyền kiểm soát (hostname: {hostname}). Đóng bot."
                    )
                    await bot.close()
        except Exception as e:
            print("⚠ Không thể kiểm tra bot.lock:", e)

    bot_lock = check_lock
    if not bot_lock.is_running():
        await register_lock()
        bot_lock.start()
