# help.py
from discord.ext import commands


def setup_help(bot):
    bot.help_command = None

    @bot.command(name="commands", aliases=["help", "cmd"])
    async def show_commands(ctx):
        msg = (
            "**🏋️ Ironman Coach Bot – Command List**\n\n"
            "• `!commands hoặc !help` – Xem danh sách lệnh 📜\n"
            "• `!motivate` – Gửi 1 câu quote động lực 💪\n"
            "• `!countdown` – Số ngày còn lại đến Ironman ⏳\n"
            "• `!show_time` – Xem thời gian đã đặt cho các lệnh 🕒\n"
            "• `!set_time` – Đặt thời gian cho các lệnh 🕒\n"
            "• `!set_time motivate 5:30 -> 22:00` - Đặt thời gian động lực từ 5:30 đến 22:00 🕒\n"
            "• `!set_time motivate loop 2` – Đặt chu kỳ lặp động lực mỗi 2 giờ 🔄\n"
            "• `!set_time countdown 5:00` – Đặt thời gian đếm ngược vào 5:00 hàng ngày 🕒\n"
            "• `!set_time report 23:50` – Đặt thời gian báo cáo check-in vào 23:50 hàng ngày 🕒\n"
            "• `!set_time rank sun 23:55` – Đặt thời gian báo cáo xếp hạng vào 23:55 chủ nhật hàng tuần 🕒\n"
            "• `!checkin` – Check-in trong ngày bằng ảnh 📸\n"
            "• `!checkin @name` – Check-in hộ trong ngày bằng ảnh (admin only) 📸\n"
            "• `!checkin @name DD-MM-YYYY` – Check-in hộ vào ngày cụ thể bằng ảnh (admin only) 📸\n"
            "• `!checkin status` – Xem ai đã check-in hôm nay ✅\n"
            "• `!checkin status DD-MM-YYYY` – Xem ai đã check-in vào ngày cụ thể ✅\n"
            "• `!rank` – Xem bảng xếp hạng check-in 🏆\n"
            "• `!rank MM-YYYY` – Xem bảng xếp hạng check-in theo tháng 🏆\n"
            "• `!rank all` – Xem bảng xếp hạng check-in alltime 🏆\n"
            "• `!backup` – Sao lưu dữ liệu lên Google Drive (admin only) 💾\n"
            "• `!restore` – Khôi phục dữ liệu từ Google Drive (admin only) 💾\n"
            "• `!ping` – Kiểm tra bot hoạt động 🏓\n"
            "• `!report today` – Tổng hợp báo cáo check-in hôm nay 📋\n"
            "• `!report DD-MM-YYYY` – Tổng hợp báo cáo check-in ngày cụ thể 📋\n"
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
