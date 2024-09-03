from flask import Flask, request, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///drinks.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)

    # Define models
    class Drink(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        description = db.Column(db.String(255))
        image = db.Column(db.String(255))
        category = db.Column(db.String(100))
        price = db.Column(db.Float, nullable=False)

    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(100), unique=True, nullable=False)
        password = db.Column(db.String(255), nullable=False)
        profile = db.Column(db.String(255))

    class Order(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        drink_id = db.Column(db.Integer, db.ForeignKey('drink.id'), nullable=False)
        quantity = db.Column(db.Integer, nullable=False)

    class Chat(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        message = db.Column(db.Text, nullable=False)
        timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Routes for Drinks
    @app.route('/drinks', methods=['GET'])
    def get_drinks():
        drinks = Drink.query.all()
        return jsonify([{
            'id': d.id,
            'name': d.name,
            'description': d.description,
            'image': d.image,
            'category': d.category,
            'price': d.price
        } for d in drinks])

    @app.route('/drinks', methods=['POST'])
    def add_drink():
        data = request.json
        new_drink = Drink(
            name=data['name'],
            description=data['description'],
            image=data['image'],
            category=data['category'],
            price=data['price']
        )
        db.session.add(new_drink)
        db.session.commit()
        return jsonify({
            'id': new_drink.id,
            'name': new_drink.name,
            'description': new_drink.description,
            'image': new_drink.image,
            'category': new_drink.category,
            'price': new_drink.price
        })

    # Routes for Users
    @app.route('/users', methods=['GET'])
    def get_users():
        users = User.query.all()
        return jsonify([{'id': u.id, 'email': u.email, 'profile': u.profile} for u in users])

    @app.route('/users', methods=['POST'])
    def add_user():
        data = request.json
        new_user = User(
            email=data['email'],
            password=data['password'],
            profile=data.get('profile', '')
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'id': new_user.id, 'email': new_user.email, 'profile': new_user.profile})

    # Routes for Orders
    @app.route('/orders', methods=['GET'])
    def get_orders():
        orders = Order.query.all()
        return jsonify([{
            'id': o.id,
            'user_id': o.user_id,
            'drink_id': o.drink_id,
            'quantity': o.quantity
        } for o in orders])

    @app.route('/orders', methods=['POST'])
    def add_order():
        data = request.json
        if not Drink.query.get(data['drink_id']) or not User.query.get(data['user_id']):
            return jsonify({'error': 'Invalid drink or user ID'}), 400
        new_order = Order(user_id=data['user_id'], drink_id=data['drink_id'], quantity=data['quantity'])
        db.session.add(new_order)
        db.session.commit()
        return jsonify({
            'id': new_order.id,
            'user_id': new_order.user_id,
            'drink_id': new_order.drink_id,
            'quantity': new_order.quantity
        })

    # Routes for Chats
    @app.route('/chats', methods=['GET'])
    def get_chats():
        chats = Chat.query.all()
        return jsonify([{
            'id': c.id,
            'user_id': c.user_id,
            'message': c.message,
            'timestamp': c.timestamp.isoformat()
        } for c in chats])

    @app.route('/chats', methods=['POST'])
    def add_chat():
        data = request.json
        new_chat = Chat(
            user_id=data['user_id'],
            message=data['message'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )
        db.session.add(new_chat)
        db.session.commit()
        return jsonify({
            'id': new_chat.id,
            'user_id': new_chat.user_id,
            'message': new_chat.message,
            'timestamp': new_chat.timestamp.isoformat()
        })

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)
