import discord
from discord.ext import commands
from utils import get_now
from database import add_user, add_checkin, get_checkin_images_by_date, get_all_users
from config import YOUR_USER_ID


def setup_checkin(bot):

    @bot.command()
    async def checkin(ctx, *args):
        from utils import get_now
        from database import add_user, add_checkin
        import re
        from datetime import datetime

        image_urls = []
        for attachment in ctx.message.attachments:
            if attachment.content_type and attachment.content_type.startswith(
                    "image/"):
                image_urls.append(attachment.url)

        if not image_urls:
            await ctx.send("⚠ Bạn cần gửi ít nhất 1 ảnh để check-in.")
            return

        # Phân tích args
        member = None
        checkin_date = get_now().strftime("%Y-%m-%d")

        if len(args) == 1:
            # Trường hợp !checkin DD-MM-YYYY (tự checkin lùi ngày)
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
                # Trường hợp !checkin @user
                member = ctx.message.mentions[
                    0] if ctx.message.mentions else None
                if ctx.author.id != YOUR_USER_ID:
                    await ctx.send(
                        "❌ Bạn không có quyền check-in hộ người khác.")
                    return

        elif len(args) == 2:
            # Trường hợp !checkin @user DD-MM-YYYY
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

        # Nếu không có ai được tag, mặc định là chính mình
        target = member or ctx.author
        user_id = str(target.id)
        username = target.display_name
        timestamp = checkin_date + " 10:00:00"

        add_user(user_id, username)
        add_checkin(user_id, timestamp, image_urls)

        if target == ctx.author and checkin_date == get_now().strftime(
                "%Y-%m-%d"):
            await ctx.send(
                f"✅ {ctx.author.mention}, bạn đã check-in lúc `{timestamp}` thành công!"
            )
        elif target == ctx.author:
            await ctx.send(
                f"✅ Bạn đã tự check-in lùi ngày `{checkin_date}` thành công.")
        else:
            await ctx.send(
                f"✅ Đã check-in hộ **{username}** cho ngày `{checkin_date}`.")

    @bot.command()
    async def checkin_status(ctx):
        date_str = get_now().strftime("%Y-%m-%d")
        all_users = get_all_users()
        checkins = get_checkin_images_by_date(date_str)

        embed = discord.Embed(title=f"📋 Trạng thái check-in ngày {date_str}",
                              color=discord.Color.green())

        for user_id, username in all_users.items():
            images = checkins.get(user_id)
            if images:
                preview = images[0]
                count = len(images)
                links = " ".join(f"[{i+1}]({url})"
                                 for i, url in enumerate(images))
                embed.add_field(name=f"{username} – {count} ảnh",
                                value=links or "-",
                                inline=False)
            else:
                embed.add_field(name=f"{username}",
                                value="❌ Chưa check-in hôm nay",
                                inline=False)

        await ctx.send(embed=embed)
