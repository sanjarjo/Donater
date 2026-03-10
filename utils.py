import time
from config import CHANNEL
from bot import bot

last_time = {}
remaining = {}
MAX_WARN = 50
COOLDOWN = 1.0

def check_spam(chat_id):
    now = time.time()
    last = last_time.get(chat_id)
    if last and now - last < COOLDOWN:
        remaining[chat_id] = remaining.get(chat_id, MAX_WARN) - 1
        if remaining[chat_id] <= 0:
            return False
        return True
    last_time[chat_id] = now
    remaining.setdefault(chat_id, MAX_WARN)
    return True

def is_subscribed(chat_id):
    try:
        member = bot.get_chat_member(CHANNEL, chat_id)
        return member.status in ["member", "creator", "administrator"]
    except:
        return False
