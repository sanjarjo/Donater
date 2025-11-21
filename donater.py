# donate_bot_full.py
# Kerakli kutubxonalar: pip install pytelegrambotapi
import telebot
from telebot import types
import time
import uuid
from flask import Flask
from threading import Thread

# ====== SOZLAMALAR (bu joyni o'zgartiring) ======
TOKEN = "8480978507:AAGt6ssU1SN3BxJN45c-jVzPQdw6CZTbSKA"
ADMIN_ID = 7390469118        # <-- o'z Telegram ID'ingiz (raqam)
CARD_NUMBER = "9860 0827 1937 9966"  # <-- to'lov uchun ko'rsatiladigan karta
# ==================================================

bot = telebot.TeleBot(TOKEN, parse_mode=None)

# Ma'lumotlar saqlanishi (xotira ichida)
user_data = {}     # chat_id -> { step, game, amount, id, zone, nick, order_id ... }
orders = {}        # order_id -> { user_id, info..., photo_file_id, admin_msg_id, status }
blocked_users = set()

# Anti-spam ma'lumotlari
last_time = {}       # chat_id -> last request time
remaining = {}       # chat_id -> remaining warnings (50...0)
MAX_WARN = 50
COOLDOWN = 2.0       # soniya

# Matn tugmalari (istalgancha o'zgartiriladi)
BTN_DONATE = " Donate qilish"
BTN_ADMIN = "’» Admin bilan aloqa"
BTN_BACK = "¸ Bekor qilish"
BTN_CONFIRM = " Tasdiqlash"
BTN_CANCEL = " Bekor qilish"

# Mobile Legends variantlari (siz bergan narxlar)
ML_AMOUNTS = [
    "11 ta almaz” 4000 so'm",
    "56 ta almaz” 12000 so'm",
    "86 ta almaz” 17000 so'm",
    "112 ta almaz” 20000 so'm",
    "Prapusk (pass) ” 23000 so'm",
    "50+50 almaz” 13000 so'm",
    "150+150 almaz” 35000 so'm",
    "250+250 almaz” 55000 so'm",
    "500+500 almaz” 120000 so'm"
]

PUBG_AMOUNTS = [
    "60 UC ” 13000 so'm"
]

# ----- yordamchi funksiyalar -----
def is_blocked(chat_id):
    return chat_id in blocked_users

def check_spam(chat_id, text=None):
    """
    Agar foydalanuvchi spam qilsa, bot ogohlantiradi va qaytaradi False.
    Agar bekor qilish yoki /start bo'lsa â€” ularni istisno qiladi (True qaytaradi).
    True -> davom etish mumkin.
    False -> davom etish mumkin emas (spam yoki blok)
    """
    # Bekor qilish va start har doim ishlasin
    if text in (BTN_BACK, BTN_CANCEL, "/start"):
        return True

    if is_blocked(chat_id):
        # agar bloklangan bo'lsa, hech narsaga javob bermaydi
        try:
            bot.send_message(chat_id, "ðŸš« Siz bloklangan ekansiz. Iltimos admin bilan bogâ€˜laning.")
        except Exception:
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
                bot.send_message(chat_id, "ðŸš« Siz juda ko'p so'rov yubordingiz. Bot sizni blokladi.")
            except Exception:
                pass
            return False
        else:
            try:
                bot.send_message(chat_id,
                    f" Iltimos, botga tez-tez so'rov yubormang!\nQolgan urinishlar: {remaining[chat_id]}")
            except Exception:
                pass
            return False
    # oxirgi vaqtni yangilaymiz va reset qilamiz (agar interval yetarli bo'lsa)
    last_time[chat_id] = now
    remaining.setdefault(chat_id, MAX_WARN)
    return True

def show_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(BTN_DONATE, BTN_ADMIN)
    bot.send_message(chat_id, " Bosh menyu:", reply_markup=markup)
    # o'sha foydalanuvchining vaqtinchalik buyurtma ma'lumotini o'chirish (sovrin)
    user_data.pop(chat_id, None)

# ----- start -----
@bot.message_handler(commands=['start'])
def handle_start(msg):
    chat_id = msg.chat.id
    # /start bekor qilish sifatida olinadi (spam-check-da istisno)
    if not check_spam(chat_id, "/start"):
        return
    show_main_menu(chat_id)

# ----- Asosiy text handler (barcha tekstlar shu yerda qayta ishlanadi) -----
@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    text = message.text.strip()

    # har doim bekor qilish tugmasi ishlashi uchun tekshirish birinchi
    if text in (BTN_BACK, BTN_CANCEL):
        # Bekor qilish: ma'lumotlarni tozalab bosh menyu
        user_data.pop(chat_id, None)
        show_main_menu(chat_id)
        return

    # Spamni tekshir (bekor qilish va /start esa tadiq)
    if not check_spam(chat_id, text):
        return

    # Agar foydalanuvchi bloklangan bo'lsa boshqa amallarni qilmang
    if is_blocked(chat_id):
        return

    # Agar foydalanuvchi bosqichda bo'lsa -> step asosida davom ettirsin
    ud = user_data.get(chat_id)

    # 1) Bosh menyu tugmalari
    if text == BTN_DONATE:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Mobile Legends", "PUBG Mobile", BTN_BACK)
        bot.send_message(chat_id, "Qaysi o'yinga donate qilmoqchisiz?", reply_markup=markup)
        return

    if text == BTN_ADMIN:
        bot.send_message(chat_id, " Admin bilan aloqa: @sanjar7729")
        return

    # 2) O'yin tanlandi
    if text == "Mobile Legends":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # har bir miqdorni alohida tugma sifatida qo'shamiz
        for amt in ML_AMOUNTS:
            markup.add(amt)
        markup.add(BTN_BACK)
        bot.send_message(chat_id, "Mobile Legends uchun miqdorni tanlang:", reply_markup=markup)
        user_data[chat_id] = {"step": "await_ml_amount", "game": "Mobile Legends"}
        return

    if text == "PUBG Mobile":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for amt in PUBG_AMOUNTS:
            markup.add(amt)
        markup.add(BTN_BACK)
        bot.send_message(chat_id, "PUBG uchun miqdorni tanlang:", reply_markup=markup)
        user_data[chat_id] = {"step": "await_pubg_amount", "game": "PUBG Mobile"}
        return

    # 3) Miqdor tanlandi (agar user_data mavjud bo'lsa va step kutilyapti)
    if ud:
        step = ud.get("step")
        # Mobile Legends miqdori tanlandi
        if step == "await_ml_amount" and text in ML_AMOUNTS:
            ud["amount"] = text
            ud["step"] = "await_id"
            bot.send_message(chat_id, "ðŸ†” Iltimos, MLBB Game ID ni kiriting (raqam):", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(BTN_BACK))
            return
        # PUBG miqdori tanlandi
        if step == "await_pubg_amount" and text in PUBG_AMOUNTS:
            ud["amount"] = text
            ud["step"] = "await_id"
            bot.send_message(chat_id, " Iltimos, PUBG Game ID ni kiriting (raqam):", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(BTN_BACK))
            return

        # ID bosqichi
        if step == "await_id":
            ud["game_id"] = text
            # MLBB talabiga qarab zona so'rovini qo'shamiz
            if ud.get("game") == "Mobile Legends":
                ud["step"] = "await_zone"
                bot.send_message(chat_id, " Zona ID kiriting:", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(BTN_BACK))
            else:
                ud["step"] = "await_nick"
                bot.send_message(chat_id, " Nick (ism) kiriting:", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(BTN_BACK))
            return

        # Zona bosqichi (faqat MLBB)
        if step == "await_zone":
            ud["zone"] = text
            ud["step"] = "await_nick"
            bot.send_message(chat_id, " Nick (ism) kiriting:", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(BTN_BACK))
            return

        # Nick bosqichi
        if step == "await_nick":
            ud["nick"] = text
            ud["step"] = "await_confirm"
            # ko'rsatish
            summary = (f" Buyurtma ma'lumoti:\n"
                       f" O'yin: {ud.get('game')}\n"
                       f" Miqdor: {ud.get('amount')}\n"
                       f" ID: {ud.get('game_id')}\n")
            if "zone" in ud:
                summary += f" Zona: {ud.get('zone')}\n"
            summary += f" Nick: {ud.get('nick')}\n\nMa'lumotlar to'g'ri bo'lsa tasdiqlang."
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(BTN_CONFIRM, BTN_CANCEL)
            bot.send_message(chat_id, summary, reply_markup=markup)
            return

        # Tasdiqlash bosqichi
        if step == "await_confirm":
            if text == BTN_CONFIRM:
                # karta ko'rsatish va keyingi bosqich - chek kutish
                ud["step"] = "waiting_photo"
                ud["order_id"] = uuid.uuid4().hex[:8]
                bot.send_message(chat_id,
                                 f" To'lov qilish uchun karta raqami:\n\n{CARD_NUMBER}\n\n"
                                 " To'lovni amalga oshirganingizdan so'ng, chek (rasm) yuboring.")
                return
            elif text == BTN_CANCEL:
                user_data.pop(chat_id, None)
                bot.send_message(chat_id, "âŒ Buyurtma bekor qilindi.")
                show_main_menu(chat_id)
                return

        # Agar user cheklash bosqichi bo'lsa va ular xabar yuborishsa (masalan matn yuborsa)
        if step == "waiting_photo":
            bot.send_message(chat_id, " Iltimos, avval to'lovni qiling va chek (rasm) yuboring yoki Bekor qilish qiling.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(BTN_BACK))
            return

    # Agar hech qanday shartiga mos kelmasa
    bot.send_message(chat_id, " Iltimos menyudan tanlang yoki /start yozing.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(BTN_BACK))

# ----- Photo (chek) handler -----
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    # Spam tekshiri (foto uchun ham qo'llanadi)
    if not check_spam(chat_id, "photo"):
        return

    ud = user_data.get(chat_id)
    if not ud or ud.get("step") != "waiting_photo":
        bot.send_message(chat_id, "— Avval buyurtma ma'lumotlarini kiriting (miqdor, ID, nick) va tasdiqlash kerak.")
        return

    # order yaratamiz
    order_id = ud.get("order_id") or uuid.uuid4().hex[:8]
    ud["order_id"] = order_id
    photo_file_id = message.photo[-1].file_id

    # order ma'lumotini saqlaymiz
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

    # foydalanuvchiga javob
    bot.send_message(chat_id, " Buyurtma qayta ishlashga topshirildi \nIltimos, sabr qiling.")
    # 2 soniya kutib bosh menyuga qaytish
    time.sleep(2)
    show_main_menu(chat_id)

    # admin ga yuborish ” inline tugmalar bilan
    caption = (f" Yangi buyurtma (ID: {order_id})\n\n"
               f" {orders[order_id]['game']}\n"
               f" {orders[order_id]['amount']}\n"
               f" {orders[order_id]['game_id']}\n"
               f" {orders[order_id].get('zone','-')}\n"
               f" {orders[order_id]['nick']}\n\n"
               f"Foydalanuvchi: @{message.from_user.username or message.from_user.first_name}")

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(" Qabul qilish", callback_data=f"accept_{order_id}"),
        types.InlineKeyboardButton(" Bekor qilish", callback_data=f"reject_{order_id}")
    )

    # adminga rasm yuboriladi va admin mesaj id saqlanadi
    admin_msg = bot.send_photo(ADMIN_ID, photo_file_id, caption=caption, reply_markup=markup)
    # saqlaymiz
    orders[order_id]["admin_msg_id"] = admin_msg.message_id
    orders[order_id]["admin_chat_id"] = ADMIN_ID

# ----- Callback (admin tugma) -----
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
        # foydalanuvchiga xabar
        try:
            bot.send_message(user_id, " Sizning buyurtmangiz yetkazib berildi bizdan harid qilganingiz uchun raxmat.")
        except Exception:
            pass
        order["status"] = "accepted"
        # adminga ham tasdiq xabari
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                 caption=call.message.caption + "\n\n Qabul qilindi", reply_markup=None)
        bot.answer_callback_query(call.id, "Buyurtma qabul qilindi.")
    else:
        # reject
        try:
            bot.send_message(user_id, " Sizning buyurtmangiz bekor qilindi. Qo'llab-quvvatlash: @sanjar7729")
        except Exception:
            pass
        order["status"] = "rejected"
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                 caption=call.message.caption + "\n\n Bekor qilindi", reply_markup=None)
        bot.answer_callback_query(call.id, "Buyurtma bekor qilindi.")

    # buyurtmani saqlab qolish uchun orders[] qoldirib qo'yiladi
    # (xohlasangiz bu yerda orderni DB ga yozish yoki olib tashlash mumkin)

# ----- Admin yordamchi buyruqlar (faqat admin uchun) -----
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
        bot.send_message(uid, "Siz admin tomonidan blokdan olindingiz. Endi botdan foydalanishingiz mumkin.")
    except:
        bot.send_message(ADMIN_ID, "Noto'g'ri ID.")

# ---- Flask qismi ----
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ishlayapti "


# Flaskâ€™ni alohida oqimda ishga tushiramiz

# ----- Botni ishga tushirish -----
# ---- Flask qismi (2-bosqichdagi kod shu joyda) ----
import os

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.infinity_polling(skip_pending=True)
