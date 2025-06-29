# loader.py
from motivate import setup_motivate
from countdown import setup_countdown
from checkin import setup_checkin
from report import setup_report, start_report_loop
from help import setup_help, setup_admin
from time_config import setup_timeconfig
from rank import setup_rank, start_rank_loop
from bot_lock import start_bot_lock


async def setup_all(bot):
    setup_motivate(bot)
    setup_countdown(bot)
    setup_checkin(bot)
    setup_report(bot)
    setup_help(bot)
    setup_admin(bot)
    setup_timeconfig(bot)
    setup_rank(bot)


async def start_loops(bot):
    start_report_loop(bot)
    start_rank_loop(bot)
    await start_bot_lock(bot)
