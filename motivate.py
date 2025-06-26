# motivate.py
import discord
import random
from discord.ext import tasks
from config import CHANNEL_ID, load_config
from utils import get_now, is_now_in_range

last_quote = None


def setup_motivate(bot):

    @tasks.loop(minutes=1)
    async def motivation_loop():
        config = load_config()
        start = config.get("motivate_start")
        end = config.get("motivate_end")
        loop_hour = int(config.get("motivate_loop", 1))

        if start and end and is_now_in_range(start, end):
            now = get_now()
            if now.minute == 0 and now.hour % loop_hour == 0:
                channel = bot.get_channel(CHANNEL_ID)
                if channel:
                    await send_motivation(channel)

    @bot.command()
    async def motivate(ctx):
        await send_motivation(ctx)

    async def send_motivation(destination):
        global last_quote
        with open("quotes.txt", "r") as f:
            quotes = [line.strip() for line in f if line.strip()]

        if len(quotes) <= 1:
            await destination.send("❗ Not enough quotes to avoid repetition.")
            return

        available = [q for q in quotes if q != last_quote]
        quote = random.choice(available)
        last_quote = quote

        await destination.send(f"🔥 {quote}")

    motivation_loop.start()
