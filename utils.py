# utils.py
from datetime import datetime
import pytz

vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")


def get_now():
    return datetime.now(vn_tz)


def is_now_in_range(start_str, end_str):
    now = get_now().time()
    start = datetime.strptime(start_str, "%H:%M").time()
    end = datetime.strptime(end_str, "%H:%M").time()

    if start <= end:
        return start <= now <= end
    else:
        # hỗ trợ khung giờ qua đêm, ví dụ 22:00 -> 06:00
        return now >= start or now <= end
