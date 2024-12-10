from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Menu, Order
import random
import os

# Create Flask app
app = Flask(__name__)

# Enable CORS
CORS(app)

# Configure SQLite database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
with app.app_context():
    db.init_app(app)
    db.create_all()

    # Seed database with test data (only if empty)
    if not Menu.query.first():  # Ensure context here
        db.session.add(Menu(name="Pizza", quantity=5, description="Cheese Pizza"))
        db.session.add(Menu(name="Pasta", quantity=10, description="Spaghetti Bolognese"))
        db.session.commit()

# Routes
@app.route('/menu', methods=['GET'])
def get_menu():
    """Fetch all menu items."""
    menu = Menu.query.all()
    return jsonify([{
        "id": item.id,
        "name": item.name,
        "quantity": item.quantity,
        "description": item.description
    } for item in menu])


@app.route('/order', methods=['POST'])
def place_order():
    """Place a new order and generate a 4-digit code."""
    data = request.json
    user_id = data.get('user_id')
    items = data.get('items')  # Expecting a list of item IDs
    code = f"{random.randint(1000, 9999)}"  # Generate a 4-digit random code

    # Create a new order
    order = Order(user_id=user_id, items=','.join(map(str, items)), code=code)
    db.session.add(order)
    db.session.commit()

    return jsonify({"order_id": order.order_id, "code": order.code})


@app.route('/verify-code', methods=['POST'])
def verify_code():
    """Verify the 4-digit code for an order."""
    data = request.json
    order_id = data.get('order_id')
    code = data.get('code')

    # Check if the order ID and code match
    order = Order.query.filter_by(order_id=order_id, code=code).first()
    if order:
        return jsonify({"status": "success"})
    return jsonify({"status": "failed"}), 401


if __name__ == '__main__':
    app.run(debug=True)

