from flask import Flask, request, jsonify
from models import db, User
from werkzeug.security import check_password_hash
from flask_cors import CORS
from models import db, Menu, Order
import random
import os

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


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

# Routes

@app.route('/login', methods=['POST'])
def login():
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

@app.route('/menu', methods=['POST'])
def add_menu_item():
    data = request.json
    name = data.get('name')
    description = data.get('description')
    quantity = data.get('quantity')

    if not all([name, description, quantity]):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    new_item = MenuItem(name=name, description=description, quantity=quantity)
    db.session.add(new_item)
    db.session.commit()

    return jsonify({"success": True, "message": "Menu item added"}), 201


if __name__ == '__main__':
    app.run(debug=True)

