import discord
import asyncio
from discord.ext import commands, tasks
from config import TOKEN
from loader import setup_all
from keepalive import keep_alive
from database import init_db
from config import YOUR_USER_ID
from data_sync import backup_to_drive, restore_from_drive
from utils import get_now

# Khởi tạo bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
init_db()
restore_from_drive()


@bot.event
async def on_ready():
    print(f"Bot is ready as {bot.user}")
    await setup_all(bot)
    auto_backup.start()


@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')


#backup len ggdrive
@bot.command()
async def backup(ctx):
    if ctx.author.id != YOUR_USER_ID:
        return await ctx.send("❌ Bạn không có quyền.")

    await ctx.defer()
    backup_to_drive()
    await ctx.send("✅ Đã sao lưu database lên Google Drive.")


last_backup_date = None


@tasks.loop(minutes=1)
async def auto_backup():
    global last_backup_date
    now = get_now()
    if now.hour == 0 and now.minute == 0:
        if last_backup_date != now.date():
            print("🌙 Đã đến 0h, bắt đầu sao lưu...")
            backup_to_drive()
            last_backup_date = now.date()


keep_alive()

bot.run(TOKEN)
