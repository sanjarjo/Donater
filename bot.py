# bot.py
import time
import uuid
import telebot
from telebot import types
from config import BOT_TOKEN, ADMIN_ID, CARD_NUMBER

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

# In-memory storage (soddalashgan)
user_data = {}     # chat_id -> { step, game, amount, game_id, zone, nick, order_id, ... }
orders = {}        # order_id -> order info
blocked_users = set()

# Anti-spam
last_time = {}     # chat_id -> last timestamp
remaining = {}     # chat_id -> remaining tries
MAX_WARN = 50
COOLDOWN = 1.0     # seconds

# Buttons / labels
BTN_DONATE = "Donate qilish"
BTN_ADMIN = "Admin bilan aloqa"
BTN_BACK = "Bekor qilish"
BTN_CONFIRM = "Tasdiqlash"
BTN_CANCEL = "Bekor qilish"

ML_AMOUNTS = [
    "11 ta — 2500 so'm",
    "56 ta — 11000 so'm",
    "86 ta — 16000 so'm",
    "112 ta — 19000 so'm",
    "Prapusk (pass) — 19500 so'm",
    "50+50 — 11000 so'm",
    "150+150 — 30000 so'm",
    "250+250 — 50000 so'm",
    "500+500 — 100000 so'm"
]

PUBG_AMOUNTS = [
    "60 UC — 12500 so'm"
]

def is_blocked(chat_id):
    return chat_id in blocked_users

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

# Start handler
@bot.message_handler(commands=['start'])
def handle_start(msg):
    chat_id = msg.chat.id
    if not check_spam(chat_id, "/start"):
        return
    show_main_menu(chat_id)

# Text handler
@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    text = message.text.strip()

    # cancel handlers
    if text in (BTN_BACK, BTN_CANCEL):
        user_data.pop(chat_id, None)
        show_main_menu(chat_id)
        return

    if not check_spam(chat_id, text):
        return

    if is_blocked(chat_id):
        return

    ud = user_data.get(chat_id)

    if text == BTN_DONATE:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Mobile Legends", "PUBG Mobile", BTN_BACK)
        bot.send_message(chat_id, "Qaysi o'yinga donate qilmoqchisiz?", reply_markup=markup)
        return

    if text == BTN_ADMIN:
        bot.send_message(chat_id, f"Admin bilan aloqa: @{ADMIN_ID}" if isinstance(ADMIN_ID, str) else f"Admin bilan aloqa: @{ADMIN_ID}")
        return

    if text == "Mobile Legends":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for amt in ML_AMOUNTS:
            markup.add(amt)
        markup.add(BTN_BACK)
        user_data[chat_id] = {"step": "await_ml_amount", "game": "Mobile Legends"}
        bot.send_message(chat_id, "Mobile Legends uchun miqdorni tanlang:", reply_markup=markup)
        return

    if text == "PUBG Mobile":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for amt in PUBG_AMOUNTS:
            markup.add(amt)
        markup.add(BTN_BACK)
        user_data[chat_id] = {"step": "await_pubg_amount", "game": "PUBG Mobile"}
        bot.send_message(chat_id, "PUBG uchun miqdorni tanlang:", reply_markup=markup)
        return

    # step flow
    if ud:
        step = ud.get("step")

        if step == "await_ml_amount" and text in ML_AMOUNTS:
            ud["amount"] = text
            ud["step"] = "await_id"
            bot.send_message(chat_id, "🆔 Iltimos, Game ID ni kiriting:", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(BTN_BACK))
            return

        if step == "await_pubg_amount" and text in PUBG_AMOUNTS:
            ud["amount"] = text
            ud["step"] = "await_id"
            bot.send_message(chat_id, "🆔 Iltimos, Game ID ni kiriting:", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(BTN_BACK))
            return

        if step == "await_id":
            ud["game_id"] = text
            if ud.get("game") == "Mobile Legends":
                ud["step"] = "await_zone"
                bot.send_message(chat_id, "🌍 Zona ID kiriting:", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(BTN_BACK))
            else:
                ud["step"] = "await_nick"
                bot.send_message(chat_id, "👤 Nick kiriting:", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(BTN_BACK))
            return

        if step == "await_zone":
            ud["zone"] = text
            ud["step"] = "await_nick"
            bot.send_message(chat_id, "👤 Nick kiriting:", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(BTN_BACK))
            return

        if step == "await_nick":
            ud["nick"] = text
            ud["step"] = "await_confirm"
            summary = (f"Buyurtma ma'lumotlari:\n"
                       f"O'yin: {ud.get('game')}\n"
                       f"Miqdor: {ud.get('amount')}\n"
                       f"ID: {ud.get('game_id')}\n")
            if "zone" in ud:
                summary += f"Zona: {ud.get('zone')}\n"
            summary += f"Nick: {ud.get('nick')}\n\nMa'lumotlar to'g'ri bo'lsa tasdiqlang."
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(BTN_CONFIRM, BTN_CANCEL)
            bot.send_message(chat_id, summary, reply_markup=markup)
            return

        if step == "await_confirm":
            if text == BTN_CONFIRM:
                ud["step"] = "waiting_photo"
                ud["order_id"] = uuid.uuid4().hex[:8]
                bot.send_message(chat_id, f"To'lov uchun karta raqami:\n\n{CARD_NUMBER}\n\nTo'lovdan so'ng chek rasm yuboring.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(BTN_BACK))
                return
            elif text == BTN_CANCEL:
                user_data.pop(chat_id, None)
                bot.send_message(chat_id, "Buyurtma bekor qilindi.")
                show_main_menu(chat_id)
                return

        if step == "waiting_photo":
            bot.send_message(chat_id, "Iltimos, chek (rasm) yuboring yoki Bekor qiling.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(BTN_BACK))
            return

    bot.send_message(chat_id, "Iltimos menyudan tanlang yoki /start yozing.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(BTN_BACK))

# Photo handler
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    if not check_spam(chat_id, "photo"):
        return

    ud = user_data.get(chat_id)
    if not ud or ud.get("step") != "waiting_photo":
        bot.send_message(chat_id, "Avval buyurtma ma'lumotlarini kiriting (miqdor, ID, nick) va tasdiqlang.")
        return

    order_id = ud.get("order_id") or uuid.uuid4().hex[:8]
    ud["order_id"] = order_id
    photo_file_id = message.photo[-1].file_id

    orders[order_id] = {
        "user_id": chat_id,
        "game": ud.get("game"),
        "amount": ud.get("amount"),
        "game_id": ud.get("game_id"),
        "zone": ud.get("zone"),
        "nick": ud.get("nick"),
        "photo_file_id": photo_file_id,
        "status": "pending"
    }

    # Foydalanuvchiga tasdiq va bosh menyuga qaytarish
    bot.send_message(chat_id, "Buyurtma qayta ishlashga topshirildi. Iltimos sabr qiling.")
    show_main_menu(chat_id)

    # Adminga rasm yuborish (inline)
    caption = (f"Yangi buyurtma (ID: {order_id})\n\n"
               f"{orders[order_id]['game']}\n"
               f"{orders[order_id]['amount']}\n"
               f"ID: {orders[order_id]['game_id']}\n"
               f"Zona: {orders[order_id].get('zone','-')}\n"
               f"Nick: {orders[order_id]['nick']}\n\n"
               f"Foydalanuvchi: @{message.from_user.username or message.from_user.first_name}")

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Qabul qilish", callback_data=f"accept_{order_id}"),
        types.InlineKeyboardButton("Bekor qilish", callback_data=f"reject_{order_id}")
    )

    try:
        admin_msg = bot.send_photo(ADMIN_ID, photo_file_id, caption=caption, reply_markup=markup)
        orders[order_id]["admin_msg_id"] = admin_msg.message_id
        orders[order_id]["admin_chat_id"] = ADMIN_ID
    except Exception as e:
        # agar adminga yuborilmasa - saqlab qo'yamiz va adminga xatolik haqida xabar yuboramiz
        print("Adminga yuborishda xato:", e)

# Callback handler (admin buttons)
@bot.callback_query_handler(func=lambda c: c.data and (c.data.startswith("accept_") or c.data.startswith("reject_")))
def handle_admin_callback(call):
    data = call.data
    action, order_id = data.split("_", 1)
    order = orders.get(order_id)
    if not order:
        bot.answer_callback_query(call.id, "Buyurtma topilmadi yoki allaqachon qayta ishlangan.")
        return

    user_id = order["user_id"]

    if action == "accept":
        try:
            bot.send_message(user_id, "✅ Sizning buyurtmangiz admin tomonidan qabul qilindi! Rahmat.")
        except:
            pass
        order["status"] = "accepted"
        try:
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=call.message.caption + "\n\n✅ Qabul qilindi", reply_markup=None)
        except:
            pass
        bot.answer_callback_query(call.id, "Buyurtma qabul qilindi.")
    else:
        try:
            bot.send_message(user_id, "❌ Sizning buyurtmangiz bekor qilindi. Qo'llab-quvvatlash: @sanjar7729")
        except:
            pass
        order["status"] = "rejected"
        try:
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=call.message.caption + "\n\n❌ Bekor qilindi", reply_markup=None)
        except:
            pass
        bot.answer_callback_query(call.id, "Buyurtma bekor qilindi.")

# Admin helper commands
@bot.message_handler(commands=['blocked'])
def cmd_blocked(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    if not blocked_users:
        bot.send_message(ADMIN_ID, "Hech kim bloklanmagan.")
        return
    lst = "\n".join(str(u) for u in blocked_users)
    bot.send_message(ADMIN_ID, f"Bloklanganlar:\n{lst}")

@bot.message_handler(commands=['unblock'])
def cmd_unblock(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    parts = msg.text.split()
    if len(parts) < 2:
        bot.send_message(ADMIN_ID, "Foydalanuvchi ID kiriting: /unblock <user_id>")
        return
    try:
        uid = int(parts[1])
        blocked_users.discard(uid)
        remaining[uid] = MAX_WARN
        last_time.pop(uid, None)
        bot.send_message(ADMIN_ID, f"{uid} blokdan olindi.")
        try:
            bot.send_message(uid, "Siz admin tomonidan blokdan olindingiz. Endi botdan foydalanishingiz mumkin.")
        except:
            pass
    except:
        bot.send_message(ADMIN_ID, "Noto'g'ri ID.")
