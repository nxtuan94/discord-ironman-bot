import discord
import asyncio
from discord.ext import commands, tasks
from utils import get_now
from database import get_checkin_images_by_date, get_all_users
from image_utils import create_collage_with_numbers
from config import LOG_CHANNEL_ID, load_config
from datetime import datetime


# Hàm gửi báo cáo hàng ngày
async def send_daily_report(channel, date_str, bot):
    all_users = get_all_users()
    checkin_data = get_checkin_images_by_date(date_str)

    # Embed tổng quát
    embed = discord.Embed(title=f"📋 Check-in ngày {date_str}",
                          color=discord.Color.blue(),
                          timestamp=get_now())
    embed.set_footer(text="Ironman Check-in System")

    for user_id, username in all_users.items():
        has_checked_in = user_id in checkin_data
        status = "✅ Đã check-in" if has_checked_in else "❌ Chưa check-in"
        embed.add_field(name=username, value=status, inline=True)

    await channel.send(embed=embed)

    # Gửi từng người (nếu có ảnh)
    for user_id, image_urls in checkin_data.items():
        if not image_urls:
            continue

        username = all_users.get(user_id, f"<@{user_id}>")
        user = await bot.fetch_user(int(user_id))
        avatar_url = user.avatar.url if user and user.avatar else user.default_avatar.url

        collage_io = create_collage_with_numbers(image_urls,
                                                 max_per_row=3,
                                                 target_height=400)
        if not collage_io:
            continue

        embed = discord.Embed(
            title=f"{username} – {len(image_urls)} ảnh ({date_str})",
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

    @bot.command()
    async def report(ctx, *, arg: str = "today"):
        arg = arg.strip().lower()

        # Xác định ngày
        if arg == "today":
            target_date = get_now().strftime("%Y-%m-%d")
        else:
            try:
                dt = datetime.strptime(arg, "%d-%m-%Y")
                target_date = dt.strftime("%Y-%m-%d")
            except ValueError:
                await ctx.send(
                    "❌ Định dạng sai. Dùng `!report today` hoặc `!report DD-MM-YYYY`"
                )
                return

        await send_daily_report(ctx.channel, target_date, bot)


report_loop = None


def start_report_loop(bot):
    global report_loop
    #loop
    @tasks.loop(minutes=1)
    async def _loop():
        now = get_now()
        hour, minute = load_report_time()
        target_date = get_now().strftime("%Y-%m-%d")

        if now.hour == hour and now.minute == minute:
            # ID của kênh bạn muốn gửi report vào (ví dụ: #general)
            channel_id = LOG_CHANNEL_ID  # <-- Thay bằng ID thật
            channel = bot.get_channel(channel_id)
            if channel:
                await send_daily_report(channel, target_date, bot)

    report_loop = _loop
    if not report_loop.is_running():
        report_loop.start()
