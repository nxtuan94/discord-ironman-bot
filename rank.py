import discord
from discord.ext import commands, tasks
from utils import get_now
from database import (get_all_users, get_user_checkin_dates, save_rank,
                      get_ranks_for_month, delete_rank_cache_for_date)
from datetime import datetime, timedelta
from config import LOG_CHANNEL_ID


def analyze_streaks(dates, filter_month=None):
    # Chuyển tất cả sang datetime.date và loại trùng
    sorted_dates = sorted(set(
        datetime.strptime(d[:10], "%Y-%m-%d").date()
        for d in dates if len(d) >= 10
    ))

    if filter_month:
        sorted_dates = [d for d in sorted_dates if d.strftime("%Y-%m") == filter_month]

    # Tính best streak
    best_streak = 0
    streak = 1
    for i in range(1, len(sorted_dates)):
        prev = sorted_dates[i - 1]
        curr = sorted_dates[i]
        if (curr - prev).days == 1:
            streak += 1
        else:
            best_streak = max(best_streak, streak)
            streak = 1
    best_streak = max(best_streak, streak) if sorted_dates else 0

    # Tính current streak (tính ngược từ hôm nay)
    today = get_now().date()
    streak = 0
    for offset in range(0, 365):
        d = today - timedelta(days=offset)
        if d in sorted_dates:
            streak += 1
        elif offset == 0:
            continue  # bỏ qua nếu chưa check-in hôm nay
        else:
            break
    current_streak = streak

    return best_streak, current_streak



def recalculate_month_ranks(month_prefix):
    users = get_all_users()
    ranks = {}

    for uid in users:
        checkin_dates = get_user_checkin_dates(uid)

        # Lọc những ngày nằm trong tháng cần tính
        month_dates = [d for d in checkin_dates if d.startswith(month_prefix)]

        # Chuyển về định dạng ngày và loại bỏ trùng lặp
        month_days = set(
            datetime.strptime(d, "%Y-%m-%d").date().isoformat()
            for d in month_dates
        )

        # Tính streak như cũ
        best, current = analyze_streaks(checkin_dates, filter_month=month_prefix)

        total = len(month_days)

        save_rank(month_prefix, uid, total, best, current)
        ranks[uid] = {
            "total": total,
            "best_streak": best,
            "current_streak": current
        }

    return ranks


def format_rank_embed(title, data, users):
    embed = discord.Embed(title=title, color=discord.Color.blurple())
    sorted_data = sorted(data.items(),
                         key=lambda x: (-x[1]["total"], -x[1]["best_streak"]))
    for i, (uid, stats) in enumerate(sorted_data, 1):
        name = users.get(uid, f"<@{uid}>")
        line = f'📅 **{stats["total"]} ngày** | 🔥 `{stats["current_streak"]}` liên tiếp | 🏆 max `{stats["best_streak"]}`'
        embed.add_field(name=f"#{i} – {name}", value=line, inline=False)
    return embed


async def send_rank_report(ctx, arg):
    users = get_all_users()
    now = get_now()
    data = {}

    if arg == "all":
        for uid in users:
            checkin_dates = get_user_checkin_dates(uid)

            # Tính best và current streak như cũ
            best, current = analyze_streaks(checkin_dates)

            # Đếm số ngày check-in duy nhất
            unique_days = set(
                datetime.strptime(d, "%Y-%m-%d").date().isoformat()
                for d in checkin_dates
            )
            total = len(unique_days)

            data[uid] = {
                "total": total,
                "best_streak": best,
                "current_streak": current
            }
        title = "📊 BẢNG XẾP HẠNG TỔNG"

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

        data = get_ranks_for_month(prefix)
        if not data:
            data = recalculate_month_ranks(prefix)

        title = f"📊 BXH tháng {prefix}"

    if all(d["total"] == 0 for d in data.values()):
        await ctx.send(f"❌ Không có dữ liệu check-in cho {arg or 'tháng này'}")
        return

    embed = format_rank_embed(title, data, users)
    await ctx.send(embed=embed)



@commands.command()
async def rank_reset(ctx, month=None):
    from utils import get_now

    if month and "-" in month:
        try:
            m, y = map(int, month.split("-"))
            date_str = f"{y}-{m:02}-01"
        except:
            await ctx.send(
                "⚠ Định dạng tháng không hợp lệ. Dùng dạng `MM-YYYY`.")
            return
    else:
        date_str = get_now().strftime("%Y-%m-01")
        month = get_now().strftime("%m-%Y")

    delete_rank_cache_for_date(date_str)
    await ctx.send(
        f"✅ Đã xóa cache BXH tháng `{date_str[:7]}`. Đang tính lại...")
    data = recalculate_month_ranks(date_str[:7])
    users = get_all_users()
    title = f"📊 BXH tháng {date_str[:7]}"
    embed = format_rank_embed(title, data, users)
    await ctx.send(embed=embed)


def setup_rank(bot):
    bot.add_command(rank_reset)

    @bot.command()
    async def rank(ctx, arg=None):
        await send_rank_report(ctx, arg)


WEEKDAY_MAP = {
    "mon": 0,
    "tue": 1,
    "wed": 2,
    "thu": 3,
    "fri": 4,
    "sat": 5,
    "sun": 6
}


def load_rank_time():
    from config import load_config

    config = load_config()

    raw_time = config.get("rank_time", "23:55")
    raw_day = config.get("rank_day", "sun")
    try:
        hour, minute = map(int, raw_time.split(":"))
        weekday = WEEKDAY_MAP[raw_day.lower()]
        return weekday, hour, minute
    except Exception as e:
        print(f"[LỖI] Đọc thời gian thất bại: {e}")
        return 6, 23, 55  # mặc định: Chủ nhật 23:55


rank_loop = None


def start_rank_loop(bot):
    global rank_loop

    @tasks.loop(minutes=1)
    async def _loop():
        now = get_now()
        weekday, hour, minute = load_rank_time()

        if now.weekday(
        ) == weekday and now.hour == hour and now.minute == minute:
            # ID của kênh bạn muốn gửi report vào (ví dụ: #general)
            channel_id = LOG_CHANNEL_ID  # <-- Thay bằng ID thật
            channel = bot.get_channel(channel_id)
            if channel:
                await send_rank_report(channel, None)

    rank_loop = _loop
    if not rank_loop.is_running():
        rank_loop.start()
