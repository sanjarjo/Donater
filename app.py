from flask import Flask, request
import telebot
from config import BOT_TOKEN
from bot import bot  # mavjud bot obyektini import qilamiz

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Bot ishlayapti — webhook server OK."

@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_data = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "OK", 200

def run_flask():
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
