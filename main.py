# main.py
from flask import Flask, request
import telebot
import os
from bot import bot  # faqat bot obyektini olamiz

app = Flask(__name__)

TOKEN = bot.token

# Render URL (o'zingizning URL’ingizni qo’ying)
WEBHOOK_URL = f"https://donater-t3xm.onrender.com/webhook/{TOKEN}"


@app.route("/", methods=["GET"])
def home():
    return "Bot webhook orqali ishlayapti — 24/7 ✔️"


# --- Telegram webhook qabul qiluvchi endpoint ---
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    json_data = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "OK", 200


if __name__ == "__main__":
    # Eski webhookni o'chirish
    bot.remove_webhook()

    # Yangi webhookni o'rnatish
    bot.set_webhook(url=WEBHOOK_URL)

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
