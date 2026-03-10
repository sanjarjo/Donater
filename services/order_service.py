from ..database import SessionLocal
from ..models.order import Order
from ..utils.order_id import generate_order_id

def create_order(data):

    db = SessionLocal()

    order = Order(

        order_number = generate_order_id(),

        user_id = data["user_id"],

        player_id = data["player_id"],

        zone_id = data["zone_id"],

        nickname = data["nickname"],

        diamond = data["diamond"],

        price = data["price"]

    )

    db.add(order)

    db.commit()

    return order
