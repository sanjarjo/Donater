# app.py
from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot ishlayapti — donat bot (24/7)."

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    # host 0.0.0.0 va port PORT bilan ishlaydi (Render uchun kerak)
    app.run(host="0.0.0.0", port=port)
