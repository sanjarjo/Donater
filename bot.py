import time
import uuid
import telebot
from telebot import types
from config import BOT_TOKEN, ADMIN_ID, CARD_NUMBER, CHANNEL

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

# In-memory storage
user_data = {}
orders = {}
blocked_users = set()

# Anti-spam
last_time = {}
remaining = {}
MAX_WARN = 50
COOLDOWN = 1.0  # seconds

# Buttons
BTN_DONATE = "Donate qilish"
BTN_ADMIN = "Admin bilan aloqa"
BTN_BACK = "Bekor qilish"
BTN_CONFIRM = "Tasdiqlash"
BTN_CANCEL = "Bekor qilish"

ML_AMOUNTS = [
    "11 ta — 3000 so'm",
    "56 ta — 12000 so'm",
    "86 ta — 17000 so'm",
    "112 ta — 20000 so'm",
    "Prapusk (pass) — 19990 so'm",
    "50+50 — 11000 so'm",
    "150+150 — 35000 so'm",
    "250+250 — 55000 so'm",
    "500+500 — 100000 so'm"
]

PUBG_AMOUNTS = [
    "60 UC — 12500 so'm"
]

# Functions
def is_blocked(chat_id):
    return chat_id in blocked_users

def is_subscribed(chat_id):
    try:
        member = bot.get_chat_member(CHANNEL, chat_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def check_spam(chat_id, text=None):
    # always allow cancels and /start
    if text in (BTN_BACK, BTN_CANCEL, "/start"):
        return True

    if is_blocked(chat_id):
        try:
            bot.send_message(chat_id, "🚫 Siz bloklangansiz. Iltimos admin bilan bog'laning.")
        except:
            pass
        return False

    now = time.time()
    last = last_time.get(chat_id)
    if last is None:
        last_time[chat_id] = now
        remaining.setdefault(chat_id, MAX_WARN)
        return True

    if now - last < COOLDOWN:
        remaining[chat_id] = remaining.get(chat_id, MAX_WARN) - 1
        last_time[chat_id] = now
        if remaining[chat_id] <= 0:
            blocked_users.add(chat_id)
            try:
                bot.send_message(chat_id, "🚫 Siz juda ko'p so'rov yubordingiz. Bot sizni blokladi.")
            except:
                pass
            return False
        else:
            try:
                bot.send_message(chat_id, f"⚠️ Iltimos, botga tez-tez so'rov yubormang!\nQolgan urinishlar: {remaining[chat_id]}")
            except:
                pass
            return False

    last_time[chat_id] = now
    remaining.setdefault(chat_id, MAX_WARN)
    return True

def show_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(BTN_DONATE, BTN_ADMIN)
    bot.send_message(chat_id, "🏠 Bosh menyu:", reply_markup=markup)
    user_data.pop(chat_id, None)
