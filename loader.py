# loader.py
from motivate import setup_motivate
from countdown import setup_countdown
from checkin import setup_checkin
from report import setup_report
from help import setup_help, setup_admin
from time_config import setup_timeconfig


async def setup_all(bot):
    setup_motivate(bot)
    setup_countdown(bot)
    setup_checkin(bot)
    setup_report(bot)
    setup_help(bot)
    setup_admin(bot)
    setup_timeconfig(bot)
