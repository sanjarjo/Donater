from bot import bot
from telebot import types
from utils import is_subscribed
from handlers.main_menu import show_main_menu
from config import CHANNEL

@bot.message_handler(commands=['start'])
def handle_start(msg):
    chat_id = msg.chat.id
    if not is_subscribed(chat_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("📢 Kanalga obuna bo'lish", url=f"https://t.me/{CHANNEL[1:]}")
        )
        bot.send_message(chat_id, "❌ Botdan foydalanish uchun kanalga obuna bo‘ling.", reply_markup=markup)
        return

    show_main_menu(chat_id)
