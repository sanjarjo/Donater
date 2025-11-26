# config.py
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable not set")

# ADMIN_ID ni Render-da environment ga qo'ysangiz xavfsiz (raqam)
ADMIN_ID = int(os.getenv("ADMIN_ID", "7390469118"))

# To'lov karta (siz bergan karta)
CARD_NUMBER = "9860 0827 1937 9966"
