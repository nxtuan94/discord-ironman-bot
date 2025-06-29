# timeconfig.py
from discord.ext import commands
from config import load_config, save_config


def setup_timeconfig(bot):
    DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    @bot.command()
    async def set_time(ctx, task: str, *, time_input: str):
        try:
            time_input = time_input.strip().lower()
            config = load_config()

            if "->" in time_input:
                # Đặt khoảng thời gian: 5:30 -> 23:00
                start_str, end_str = map(str.strip, time_input.split("->"))
                start_parts = start_str.split(":")
                end_parts = end_str.split(":")

                if len(start_parts) != 2 or len(end_parts) != 2:
                    raise ValueError("Sai định dạng giờ. Dùng HH:MM")

                start_hour, start_min = int(start_parts[0]), int(
                    start_parts[1])
                end_hour, end_min = int(end_parts[0]), int(end_parts[1])

                if not (0 <= start_hour <= 23 and 0 <= start_min <= 59):
                    raise ValueError("Giờ bắt đầu không hợp lệ.")
                if not (0 <= end_hour <= 23 and 0 <= end_min <= 59):
                    raise ValueError("Giờ kết thúc không hợp lệ.")

                config = load_config()
                config[f"{task}_start"] = f"{start_hour:02d}:{start_min:02d}"
                config[f"{task}_end"] = f"{end_hour:02d}:{end_min:02d}"
                save_config(config)

                await ctx.send(
                    f"✅ Đã đặt thời gian `{task}` từ {start_hour:02d}:{start_min:02d} → {end_hour:02d}:{end_min:02d}"
                )

            elif "loop" in time_input:
                # Trường hợp đặt chu kỳ lặp
                parts = time_input.split()

                if len(parts) != 2 or not parts[1].isdigit():
                    raise ValueError("Sai định dạng. Dùng: loop 2")
                loop_val = int(parts[1])
                config = load_config()
                config[f"{task}_loop"] = loop_val
                save_config(config)
                await ctx.send(
                    f"✅ Đã đặt thời gian lặp `{task}` mỗi {loop_val} giờ.")

            else:
                parts = time_input.split()

                if len(parts) == 2 and parts[0] in DAYS:
                    # Trường hợp có ngày trong tuần: sun 23:50
                    day = parts[0]
                    hour_str = parts[1]
                    hour, minute = map(int, hour_str.split(":"))

                    if not (0 <= hour <= 23 and 0 <= minute <= 59):
                        raise ValueError("Giờ không hợp lệ.")

                    config[f"{task}_day"] = day
                    config[f"{task}_time"] = f"{hour:02d}:{minute:02d}"
                    save_config(config)

                    await ctx.send(
                        f"✅ Đã đặt thời gian `{task}` vào lúc {hour:02d}:{minute:02d} mỗi `{day}`"
                    )

                elif len(parts) == 1 and ":" in parts[0]:
                    # Trường hợp chỉ có giờ: 23:55
                    hour, minute = map(int, parts[0].split(":"))
                    if not (0 <= hour <= 23 and 0 <= minute <= 59):
                        raise ValueError("Giờ không hợp lệ.")

                    config[f"{task}_time"] = f"{hour:02d}:{minute:02d}"
                    save_config(config)

                    await ctx.send(
                        f"✅ Đã đặt thời gian `{task}` vào lúc {hour:02d}:{minute:02d}"
                    )

                else:
                    raise ValueError("Định dạng không hợp lệ.")

        except Exception as e:
            await ctx.send(f"⚠️ Lỗi: {str(e)}.\nVí dụ:\n"
                           "- `!set_time motivate 5:30 -> 23:00`\n"
                           "- `!set_time reminder 5:00`\n"
                           "- `!set_time motivate loop 2`\n"
                           "- `!set_time report 23:55`\n"
                           "- `!set_time rank sun 23:50`")

    @bot.command(name="show_time")
    async def show_time(ctx):
        config = load_config()
        msg = "**⏰ Thời gian đã cài đặt:**\n"

        for key in sorted(config.keys()):
            if key.endswith("_start"):
                base = key.replace("_start", "")
                start = config.get(f"{base}_start")
                end = config.get(f"{base}_end", "???")
                msg += f"• `{base}`: {start} → {end}\n"

            elif key.endswith("_time") and f"{key[:-5]}_day" in config:
                base = key.replace("_time", "")
                day = config.get(f"{base}_day")
                time = config.get(key)
                msg += f"• `{base}`: {time} mỗi `{day}`\n"

            elif key.endswith("_time"):
                base = key.replace("_time", "")
                time = config.get(key)
                msg += f"• `{base}`: {time}\n"

            elif key.endswith("_loop"):
                base = key.replace("_loop", "")
                loop = config.get(key)
                msg += f"• `{base}`: mỗi {loop} giờ\n"

        await ctx.send(msg)
