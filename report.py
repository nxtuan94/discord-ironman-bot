import discord
import asyncio
from discord.ext import commands, tasks
from utils import get_now
from database import get_checkin_images_by_date, get_all_users
from image_utils import create_collage_with_numbers
from config import LOG_CHANNEL_ID, load_config


# Hàm gửi báo cáo hàng ngày
async def send_daily_report(channel):

    today = get_now().strftime("%Y-%m-%d")
    all_users = get_all_users()
    checkin_data = get_checkin_images_by_date(today)

    # Embed tổng quát trạng thái check-in
    status_embed = discord.Embed(title=f"📋 Trạng thái check-in ngày {today}",
                                 color=discord.Color.blue(),
                                 timestamp=get_now())
    status_embed.set_footer(text="Ironman Check-in System")

    for user_id, username in all_users.items():
        has_checked_in = user_id in checkin_data
        status = "✅ Đã check-in" if has_checked_in else "❌ Chưa check-in"
        status_embed.add_field(name=username, value=status, inline=True)

    await channel.send(embed=status_embed)
    # Gửi từng embed riêng kèm ảnh ghép
    for user_id, image_urls in checkin_data.items():
        if not image_urls:
            continue

        username = all_users.get(user_id, f"<@{user_id}>")
        user = await channel.bot.fetch_user(int(user_id))
        avatar_url = user.avatar.url if user and user.avatar else user.default_avatar.url

        collage_io = create_collage_with_numbers(image_urls,
                                                 max_per_row=3,
                                                 target_height=400)
        if not collage_io:
            continue

        embed = discord.Embed(title=f"{username} – {len(image_urls)} ảnh",
                              color=discord.Color.green(),
                              timestamp=get_now())
        embed.set_author(name=username, icon_url=avatar_url)
        embed.set_footer(text="Ironman Check-in System")
        embed.set_image(url="attachment://collage.jpg")

        links = "\n".join(f"[{i+1}]({url})"
                          for i, url in enumerate(image_urls))
        embed.add_field(name="📸 Danh sách ảnh", value=links, inline=False)

        file = discord.File(collage_io, filename="collage.jpg")
        await channel.send(embed=embed, file=file)


def load_report_time():
    config = load_config()
    raw_time = config.get("report_time", "23:50")
    try:
        hour, minute = map(int, raw_time.split(":"))
        return hour, minute
    except Exception as e:
        print(f"[LỖI] Đọc thời gian thất bại: {e}")
        return 23, 50


def setup_report(bot):

    #loop
    @tasks.loop(minutes=1)
    async def daily_report_loop():
        now = get_now()
        hour, minute = load_report_time()

        if now.hour == hour and now.minute == minute:
            # ID của kênh bạn muốn gửi report vào (ví dụ: #general)
            channel_id = LOG_CHANNEL_ID  # <-- Thay bằng ID thật
            channel = bot.get_channel(channel_id)
            if channel:
                await send_daily_report(channel)

    @bot.event
    async def on_ready():
        if not daily_report_loop.is_running():
            daily_report_loop.start()

    @bot.command()
    async def report_today(ctx):
        await send_daily_report(ctx.channel)
