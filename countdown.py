# countdown.py
import discord
from discord.ext import tasks
from datetime import datetime
from config import CHANNEL_ID, load_config
from utils import get_now, vn_tz

EVENT_DATE = vn_tz.localize(datetime(2026, 5, 10))


def setup_countdown(bot):

    @tasks.loop(minutes=1)
    async def countdown_loop():
        config = load_config()
        now = get_now().time()
        time_str = config.get("countdown_time")

        if time_str:
            target_time = datetime.strptime(time_str, "%H:%M").time()
            if now.hour == target_time.hour and now.minute == target_time.minute:
                channel = bot.get_channel(CHANNEL_ID)
                if channel:
                    await send_countdown(channel)

    @bot.command()
    async def countdown(ctx):
        await send_countdown(ctx)

    async def send_countdown(destination):
        now = get_now()
        days_left = (EVENT_DATE - now).days
        if days_left >= 0:
            await destination.send(
                f"⏳ {days_left} days left until Ironman 2026! Keep pushing hard! 💪"
            )

    countdown_loop.start()
