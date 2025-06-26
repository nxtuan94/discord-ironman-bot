# help.py
from discord.ext import commands


def setup_help(bot):
    bot.help_command = None

    @bot.command(name="commands", aliases=["help", "cmd"])
    async def show_commands(ctx):
        msg = (
            "**🏋️ Ironman Coach Bot – Command List**\n\n"
            "• `!commands` – Xem danh sách lệnh 📜\n"
            "• `!motivate` – Gửi 1 câu quote động lực 💪\n"
            "• `!countdown` – Số ngày còn lại đến Ironman ⏳\n"
            "• `!set_time` – Đặt thời gian cho các lệnh 🕒\n"
            "• `!set_time motivate 5:30 -> 22:00` - Đặt thời gian động lực từ 5:30 đến 22:00 🕒\n"
            "• `!set_time motivate loop 2` – Đặt chu kỳ lặp động lực mỗi 2 giờ 🔄\n"
            "• `!set_time countdown 5:00` – Đặt thời gian đếm ngược vào 5:00 hàng ngày 🕒\n"
            "• `!checkin` – Check-in trong ngày bằng ảnh 📸\n"
            "• `!checkin_status` – Xem ai đã check-in hôm nay ✅\n"
            "• `!report_today` – Tổng hợp báo cáo check-in hôm nay 📋\n"
            "• `!clear [amount]` – Xoá [amount] tin nhắn gần nhất (mặc định: 100) 🧹\n"
            "• `!clear_all` – Xoá tất cả tin nhắn trong kênh 🧹\n"
            # Thêm các lệnh khác vào đây
        )
        await ctx.send(msg)


def setup_admin(bot):

    @bot.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(ctx, amount: int = 100):
        """Xoá [amount] tin nhắn gần nhất (mặc định: 100)."""
        await ctx.channel.purge(limit=amount)
        msg = await ctx.send(f"🧹 Đã xoá {amount} tin nhắn!")
        await msg.delete(delay=2)  # Xoá luôn tin nhắn thông báo sau 2s

    @bot.command()
    @commands.has_permissions(manage_messages=True)
    async def clear_all(ctx):
        deleted = 0
        while True:
            msgs = await ctx.channel.purge(limit=100)
            deleted += len(msgs)
            if len(msgs) < 100:
                break
        msg = await ctx.send(f"🧹 Đã xoá tổng cộng {deleted} tin nhắn!")
        await msg.delete(delay=3)
