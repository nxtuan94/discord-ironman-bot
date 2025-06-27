import discord
import asyncio
from discord.ext import commands, tasks
from config import TOKEN
from loader import setup_all
from keepalive import keep_alive
from database import init_db
from drive_uploader import create_backup_zip, upload_to_drive
from config import YOUR_USER_ID

# Khởi tạo bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
init_db()


@bot.event
async def on_ready():
    print(f"Bot is ready as {bot.user}")
    await setup_all(bot)
    # Gọi khi bot khởi động
    auto_backup.start()


@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')


#backup len ggdrive
@bot.command()
async def backup(ctx):
    if ctx.author.id != YOUR_USER_ID:
        return await ctx.send("❌ Bạn không có quyền.")

    zip_file = create_backup_zip()
    upload_to_drive(zip_file)
    await ctx.send("✅ Đã sao lưu file `checkin.db` lên Google Drive.")


# Tự động gọi backup mỗi ngày 1 lần
@tasks.loop(hours=24)
async def auto_backup():
    print("🔁 Đang tự động sao lưu lên Google Drive...")
    zip_file = create_backup_zip()
    upload_to_drive(zip_file)


@auto_backup.before_loop
async def before_auto_backup():
    await bot.wait_until_ready()
    print("✅ Tự động backup sẽ chạy sau khi bot sẵn sàng.")


keep_alive()

bot.run(TOKEN)
