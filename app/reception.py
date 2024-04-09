from flask import Flask, request, jsonify
from functools import wraps
from models import User, DailyMenu, Food, MonthlyMenu, Order, OrderItem, db
import jwt
from auth import token_required

app = Flask(_name_)
app.config['SECRET_KEY'] = 'your_secret_key'

# Token verification decorator
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid'}), 401

        return func(current_user, *args, **kwargs)

    return decorated

@app.route('/reception-login', methods=['POST'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return jsonify({'message': 'Could not verify'}), 401

    user = User.query.filter_by(username=auth.username).first()

    if not user:
        return jsonify({'message': 'User not found'}), 401

    if user.password != auth.password:
        return jsonify({'message': 'Invalid password'}), 401

    token = jwt.encode({'user_id': user.id}, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'token': token})


# Show monthly menu endpoint
@app.route('/monthly-menu', methods=['GET'])
@token_required
def show_monthly_menu(current_user):
    monthly_menu_items = MonthlyMenu.query.all()
    food_details = []

    for monthly_menu in monthly_menu_items:
        food = Food.query.get(monthly_menu.food_id)
        food_dict = {
            'food_id': monthly_menu.food_id,
            'item_name': food.item_name,
            'bought_count': food.bought_count,
            'price': food.price
        }
        food_details.append(food_dict)

    return jsonify({'monthly_menu': food_details}), 200

# Show daily menu endpoint
@app.route('/daily-menu', methods=['GET'])
@token_required
def show_daily_menu(current_user):
    daily_menu_items = DailyMenu.query.all()
    food_details = []

    for daily_menu in daily_menu_items:
        food = Food.query.get(daily_menu.food_id)
        food_dict = {
            'food_id': daily_menu.food_id,
            'item_name': food.item_name,
            'bought_count': food.bought_count,
            'price': food.price
        }
        food_details.append(food_dict)

    return jsonify({'daily_menu': food_details}), 200

# Delete daily menu item endpoint
@app.route('/delete-daily-menu/<int:food_id>', methods=['DELETE'])
@token_required
def delete_daily_menu(current_user, food_id):
    if current_user.id != 1:
        return jsonify({'message': 'Unauthorized access'}), 403

    item_to_delete = DailyMenu.query.get(food_id)

    if not item_to_delete:
        return jsonify({'message': 'Food item not found'}), 404

    try:
        db.session.delete(item_to_delete)
        db.session.commit()
        return jsonify({'message': 'Food item deleted successfully'}), 200
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({'message': 'Failed to delete food item'}), 500

# Add food items endpoint
@app.route('/add-food-items', methods=['POST'])
@token_required
def add_food_items(current_user):
    if current_user.id != 1:
        return jsonify({'message': 'Unauthorized access'}), 403

    data = request.json
    food_id = data.get('food_id')
    item_name = data.get('item_name')
    bought_count = data.get('bought_count')
    price = data.get('price')

    new_food_item = DailyMenu(food_id=food_id, item_name=item_name, bought_count=bought_count, price=price)

    try:
        db.session.add(new_food_item)
        db.session.commit()
        return jsonify({'message': f'{item_name} added successfully'}), 200
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({'message': 'Failed to add food item'}), 500