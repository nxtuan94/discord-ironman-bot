import discord
from discord.ext import commands
from utils import get_now
from database import add_user, add_checkin, get_checkin_images_by_date, get_all_users, delete_rank_cache_for_date
from config import YOUR_USER_ID

from datetime import datetime
import re


def setup_checkin(bot):

    @bot.command()
    async def checkin(ctx, *args):
        from utils import get_now
        from datetime import datetime

        if args and args[0].lower() == "status":
            # Xử lý lệnh checkin status
            if len(args) == 2:
                try:
                    d = datetime.strptime(args[1], "%d-%m-%Y")
                    date_key = d.strftime("%Y-%m-%d")
                except:
                    await ctx.send(
                        "⚠ Định dạng ngày không hợp lệ. Dùng DD-MM-YYYY.")
                    return
            else:
                date_key = get_now().strftime("%Y-%m-%d")

            all_users = get_all_users()
            checkin_data = get_checkin_images_by_date(date_key)

            embed = discord.Embed(
                title=f"📋 Trạng thái check-in ngày {date_key}",
                color=discord.Color.green())
            embed.set_footer(text="Ironman Check-in System")

            for user_id, username in all_users.items():
                image_urls = checkin_data.get(user_id)
                if image_urls:
                    links = " ".join(f"[{i+1}]({url})"
                                     for i, url in enumerate(image_urls))
                    value = f"✅ {len(image_urls)} ảnh {links}"
                else:
                    value = "❌ Chưa check-in"
                embed.add_field(name=username, value=value, inline=False)

            await ctx.send(embed=embed)
            return  # kết thúc lệnh nếu là checkin status

        # ======= Phần checkin bình thường phía dưới giữ nguyên =======

        is_test = False
        if args and args[0].lower() == "test":
            is_test = True
            args = args[1:]

        image_urls = []
        if not is_test:
            for attachment in ctx.message.attachments:
                if attachment.content_type and attachment.content_type.startswith(
                        "image/"):
                    image_urls.append(attachment.url)

            if not image_urls:
                await ctx.send("⚠ Bạn cần gửi ít nhất 1 ảnh để check-in.")
                return

        member = None
        checkin_date = get_now().strftime("%Y-%m-%d")
        checkin_time = get_now().strftime("%H:%M:%S")

        if len(args) == 1:
            if re.match(r"\d{2}-\d{2}-\d{4}", args[0]):
                if ctx.author.id != YOUR_USER_ID:
                    await ctx.send("❌ Bạn không có quyền check-in lùi ngày.")
                    return
                try:
                    d = datetime.strptime(args[0], "%d-%m-%Y")
                    checkin_date = d.strftime("%Y-%m-%d")
                except:
                    await ctx.send(
                        "⚠ Định dạng ngày không hợp lệ. Dùng DD-MM-YYYY.")
                    return
            else:
                member = ctx.message.mentions[
                    0] if ctx.message.mentions else None
                if ctx.author.id != YOUR_USER_ID:
                    await ctx.send(
                        "❌ Bạn không có quyền check-in hộ người khác.")
                    return

        elif len(args) == 2:
            member = ctx.message.mentions[0] if ctx.message.mentions else None
            if ctx.author.id != YOUR_USER_ID:
                await ctx.send(
                    "❌ Bạn không có quyền check-in hộ hoặc chỉnh ngày.")
                return
            try:
                d = datetime.strptime(args[1], "%d-%m-%Y")
                checkin_date = d.strftime("%Y-%m-%d")
            except:
                await ctx.send(
                    "⚠ Định dạng ngày không hợp lệ. Dùng DD-MM-YYYY.")
                return

        target = member or ctx.author
        user_id = str(target.id)
        username = target.display_name
        timestamp = f"{checkin_date} {checkin_time}"

        if not is_test:
            add_user(user_id, username)
            add_checkin(user_id, timestamp, image_urls)

            today_str = get_now().strftime("%Y-%m-%d")
            if checkin_date != today_str:
                delete_rank_cache_for_date(checkin_date)

        await ctx.send(
            f"✅ Đã check-in thành công cho {target.display_name} vào ngày {checkin_date}."
        )
