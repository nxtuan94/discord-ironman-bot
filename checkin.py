# checkin.py
import os
import json
import discord
from discord.ext import commands
from utils import get_now

CHECKIN_FILE = "checkin.json"


def load_checkin():
    if not os.path.exists(CHECKIN_FILE) or os.path.getsize(CHECKIN_FILE) == 0:
        return {}
    with open(CHECKIN_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}


def save_checkin(data):
    with open(CHECKIN_FILE, "w") as f:
        json.dump(data, f)


def setup_checkin(bot):

    @bot.command()
    async def checkin(ctx):
        today = get_now().strftime("%Y-%m-%d")
        user_id = str(ctx.author.id)

        if not ctx.message.attachments:
            await ctx.send("❗ Bạn phải đính kèm ít nhất 1 ảnh để check-in.")
            return

        checkin_data = load_checkin()
        if today not in checkin_data:
            checkin_data[today] = {}

        if user_id not in checkin_data[today]:
            checkin_data[today][user_id] = []

        for attachment in ctx.message.attachments:
            checkin_data[today][user_id].append(attachment.url)

        save_checkin(checkin_data)

        await ctx.send(f"📸 {ctx.author.display_name} đã check-in! "
                       f"Đã gửi {len(ctx.message.attachments)} ảnh. "
                       f"Tổng số: {len(checkin_data[today][user_id])}")

    @bot.command()
    async def checkin_status(ctx):
        today = get_now().strftime("%Y-%m-%d")
        checkin_data = load_checkin()
        today_checkins = checkin_data.get(today, {})

        embed = discord.Embed(title=f"📌 Check-in status – {today}",
                              color=0x3399ff,
                              timestamp=get_now())
        embed.set_footer(text="Ironman Check-in System")

        if not today_checkins:
            embed.description = "😴 Chưa ai check-in hôm nay."
        else:
            for user_id, images in today_checkins.items():
                user = await bot.fetch_user(int(user_id))
                name = user.display_name if user else f"<@{user_id}>"
                value = " ".join(f"[{i}]({img})"
                                 for i, img in enumerate(images, 1))
                embed.add_field(name=f"{name} – {len(images)} ảnh",
                                value=value.strip(),
                                inline=False)

        await ctx.send(embed=embed)
