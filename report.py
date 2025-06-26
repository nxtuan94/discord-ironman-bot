# report.py
import discord
from discord.ext import commands, tasks
from utils import get_now
from checkin import load_checkin
from config import LOG_CHANNEL_ID


async def generate_checkin_embeds(date_str, bot):
    checkin_data = load_checkin()
    checkins = checkin_data.get(date_str, {})
    if not checkins:
        return []

    embeds = []
    for user_id, images in checkins.items():
        user = await bot.fetch_user(int(user_id))
        name = user.display_name if user else f"<@{user_id}>"
        avatar_url = user.avatar.url if user and user.avatar else user.default_avatar.url

        embed = discord.Embed(title=f"{name} – {len(images)} ảnh",
                              color=0x00cc99,
                              timestamp=get_now())
        embed.set_author(name=name, icon_url=avatar_url)
        embed.set_footer(text="Ironman Check-in System")

        if images:
            embed.set_image(url=images[0])
        if len(images) > 1:
            links = " ".join(f"[{i+1}]({url})"
                             for i, url in enumerate(images[1:]))
            embed.add_field(name="Ảnh khác", value=links, inline=False)

        embeds.append(embed)
    return embeds


def setup_report(bot):

    @bot.command()
    async def report_today(ctx):
        today = get_now().strftime("%Y-%m-%d")
        embeds = await generate_checkin_embeds(today, bot)

        if not embeds:
            await ctx.send(
                f"📋 **Tổng hợp check-in ngày {today}**\n😴 Không ai check-in hôm nay."
            )
            return

        await ctx.send(f"📋 **Tổng hợp check-in ngày {today}:**")
        for embed in embeds:
            await ctx.send(embed=embed)

    @tasks.loop(minutes=1)
    async def daily_checkin_report_loop():
        now = get_now()
        if now.hour == 22 and now.minute == 0:
            channel = bot.get_channel(LOG_CHANNEL_ID)
            if channel:
                today = get_now().strftime("%Y-%m-%d")
                embeds = await generate_checkin_embeds(today, bot)
                if not embeds:
                    await channel.send(
                        f"📋 **Tổng hợp check-in ngày {today}**\n😴 Không ai check-in hôm nay."
                    )
                else:
                    await channel.send(f"📋 **Tổng hợp check-in ngày {today}:**"
                                       )
                    for embed in embeds:
                        await channel.send(embed=embed)

    daily_checkin_report_loop.start()
