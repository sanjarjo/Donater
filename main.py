# main.py
import threading
from app import run_flask
from bot import run_bot

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    flask_thread.join()
    bot_thread.join()
