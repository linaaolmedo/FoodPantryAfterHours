from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import random

# Import db and models from models.py
from models import db, Menu, Order, User

# Create Flask app
app = Flask(__name__)

# Enable CORS
CORS(app)

# Configure SQLite database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Create tables within the application context
with app.app_context():
    db.create_all()


# Routes
@app.route('/routes', methods=['GET'])
def list_routes():
    """List all routes for debugging."""
    return jsonify([str(rule) for rule in app.url_map.iter_rules()])


@app.route('/login', methods=['POST'])
def login():
    """User login route."""
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        return jsonify({"success": True, "message": "Login successful"}), 200

    return jsonify({"success": False, "message": "Invalid email or password"}), 401


@app.route('/menu', methods=['GET'])
def get_menu():
    """Fetch all menu items."""
    menu = Menu.query.all()
    return jsonify([{
        "id": item.id,
        "name": item.name,
        "quantity": item.quantity,
        "description": item.description
    } for item in menu]), 200


@app.route('/menu', methods=['POST'])
def add_menu_item():
    """Add a new menu item."""
    data = request.json
    name = data.get('name')
    description = data.get('description')
    quantity = data.get('quantity')

    if not all([name, description, quantity]):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    new_item = Menu(name=name, description=description, quantity=quantity)
    db.session.add(new_item)
    db.session.commit()

    return jsonify({"success": True, "message": "Menu item added"}), 201


@app.route('/order', methods=['POST'])
def place_order():
    """Place a new order and generate a 4-digit code."""
    data = request.json
    user_id = data.get('user_id')
    items = data.get('items')  # Expecting a list of item IDs
    code = f"{random.randint(1000, 9999)}"  # Generate a 4-digit random code

    if not user_id or not items:
        return jsonify({"success": False, "message": "User ID and items are required"}), 400

    # Create a new order
    order = Order(user_id=user_id, items=','.join(map(str, items)), code=code)
    db.session.add(order)
    db.session.commit()

    return jsonify({"success": True, "code": code}), 201


@app.route('/verify-code', methods=['POST'])
def verify_code():
    """Verify the 4-digit code for an order."""
    data = request.json
    order_id = data.get('order_id')
    code = data.get('code')

    if not order_id or not code:
        return jsonify({"success": False, "message": "Order ID and code are required"}), 400

    # Check if the order ID and code match
    order = Order.query.filter_by(order_id=order_id, code=code).first()
    if order:
        return jsonify({"success": True, "message": "Code verified"}), 200
    return jsonify({"success": False, "message": "Invalid code"}), 401


if __name__ == '__main__':
    app.run(debug=True)

