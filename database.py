import sqlite3

conn = sqlite3.connect('data/db.sqlite', check_same_thread=False)
cursor = conn.cursor()

# Foydalanuvchilar
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    chat_id INTEGER PRIMARY KEY,
    blocked INTEGER DEFAULT 0
)
""")

# Buyurtmalar
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    chat_id INTEGER,
    game TEXT,
    amount TEXT,
    game_id TEXT,
    zone TEXT,
    nick TEXT,
    status TEXT,
    photo_file_id TEXT
)
""")
conn.commit()

def add_order(order):
    cursor.execute("""
    INSERT INTO orders(order_id, chat_id, game, amount, game_id, zone, nick, status, photo_file_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        order['order_id'], order['chat_id'], order['game'], order['amount'], 
        order.get('game_id'), order.get('zone'), order.get('nick'), order['status'], order['photo_file_id']
    ))
    conn.commit()

def get_user_orders(chat_id):
    cursor.execute("SELECT * FROM orders WHERE chat_id=?", (chat_id,))
    return cursor.fetchall()
