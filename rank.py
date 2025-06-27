import discord
from discord.ext import commands
from utils import get_now
from database import (get_all_users, get_user_checkin_dates, save_rank,
                      get_ranks_for_month)
from datetime import datetime, timedelta


def analyze_streaks(dates, filter_month=None):
    sorted_dates = sorted(dates)
    best_streak = current_streak = 0

    if filter_month:
        sorted_dates = [d for d in sorted_dates if d.startswith(filter_month)]

    # Best streak
    streak = 1
    for i in range(1, len(sorted_dates)):
        prev = datetime.strptime(sorted_dates[i - 1], "%Y-%m-%d")
        curr = datetime.strptime(sorted_dates[i], "%Y-%m-%d")
        if (curr - prev).days == 1:
            streak += 1
        else:
            best_streak = max(best_streak, streak)
            streak = 1
    best_streak = max(best_streak, streak) if sorted_dates else 0

    # Current streak
    today = get_now().date()
    streak = 0
    for offset in range(0, 365):
        d = today - timedelta(days=offset)
        d_str = d.strftime("%Y-%m-%d")
        if d_str in dates:
            streak += 1
        else:
            break
    current_streak = streak

    return best_streak, current_streak


def format_rank_embed(title, data, users):
    embed = discord.Embed(title=title, color=discord.Color.blurple())
    sorted_data = sorted(data.items(),
                         key=lambda x: (-x[1]["total"], -x[1]["best_streak"]))
    for i, (uid, stats) in enumerate(sorted_data, 1):
        name = users.get(uid, f"<@{uid}>")
        line = f'📅 **{stats["total"]} ngày** | 🔥 `{stats["current_streak"]}` liên tiếp | 🏆 max `{stats["best_streak"]}`'
        embed.add_field(name=f"#{i} – {name}", value=line, inline=False)
    return embed


def setup_rank(bot):

    @bot.command()
    async def rank(ctx, arg=None):
        users = get_all_users()
        now = get_now()
        data = {}

        if arg == "all":
            for uid in users:
                checkin_dates = get_user_checkin_dates(uid)
                best, current = analyze_streaks(checkin_dates)
                total = len(checkin_dates)
                data[uid] = {
                    "total": total,
                    "best_streak": best,
                    "current_streak": current
                }
            title = "📊 BẢNG XẾP HẠNG TỔNG THỂ"

        else:
            if arg and "-" in arg:
                try:
                    month, year = map(int, arg.split("-"))
                    prefix = f"{year}-{month:02}"
                except:
                    await ctx.send(
                        "⚠ Định dạng tháng không hợp lệ. Dùng dạng `MM-YYYY`.")
                    return
            else:
                prefix = now.strftime("%Y-%m")

            # thử đọc từ ranks cache
            data = get_ranks_for_month(prefix)
            if not data:
                for uid in users:
                    checkin_dates = get_user_checkin_dates(uid)
                    month_dates = [
                        d for d in checkin_dates if d.startswith(prefix)
                    ]
                    best, current = analyze_streaks(checkin_dates, prefix)
                    total = len(month_dates)
                    data[uid] = {
                        "total": total,
                        "best_streak": best,
                        "current_streak": current
                    }
                    # Lưu vào bảng ranks
                    save_rank(prefix, uid, total, best, current)

            title = f"📊 BXH tháng {prefix}"

        if all(d["total"] == 0 for d in data.values()):
            await ctx.send(
                f"❌ Không có dữ liệu check-in cho {arg or 'tháng này'}")
            return

        embed = format_rank_embed(title, data, users)
        await ctx.send(embed=embed)
