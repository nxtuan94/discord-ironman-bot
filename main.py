import discord
from discord.ext import commands
from config import TOKEN
from loader import setup_all

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Bot is ready as {bot.user}")
    await setup_all(bot)


bot.run(TOKEN)
