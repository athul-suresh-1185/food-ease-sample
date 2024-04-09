from flask import Flask, request, jsonify
from functools import wraps
from models import User, Food, MonthlyMenu, Order, OrderItem, db
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


# Add food items endpoint
@app.route('/add-food-items', methods=['POST'])
@token_required
def add_food_items(current_user):
    if current_user.id != 1:
        return jsonify({'message': 'Unauthorized access'}), 403

    data = request.json
    food_id = data.get('product_id')
    item_name = data.get('product_name')
    price = data.get('price')

    new_food_item = MonthlyMenu(food_id=food_id, item_name=item_name, price=price)

    try:
        db.session.add(new_food_item)
        db.session.commit()
        return jsonify({'message': f'{item_name} added successfully'}), 200
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({'message': 'Failed to add food item'}), 500

# Food items endpoint
@app.route('/food-items', methods=['GET'])
@token_required
def get_food_items(current_user):
    if current_user.id != 1:
        return jsonify({'message': 'Unauthorized access'}), 403

    items = MonthlyMenu.query.order_by(MonthlyMenu.date_added).all()
    food_details = [{'food_id': item.food_id, 'item_name': item.item_name, 'price': item.price} for item in items]

    return jsonify({'food_items': food_details}), 200

# Update food item endpoint
@app.route('/update-item/<int:food_id>', methods=['PUT'])
@token_required
def update_item(current_user, food_id):
    if current_user.id != 1:
        return jsonify({'message': 'Unauthorized access'}), 403

    data = request.json
    item_to_update = MonthlyMenu.query.get(food_id)

    if not item_to_update:
        return jsonify({'message': 'Food item not found'}), 404

    item_to_update.item_name = data.get('product_name', item_to_update.item_name)
    item_to_update.price = data.get('price', item_to_update.price)

    try:
        db.session.commit()
        return jsonify({'message': f'Food item with ID {food_id} updated successfully'}), 200
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({'message': 'Failed to update food item'}), 500

# Delete food item endpoint
@app.route('/delete-item/<int:food_id>', methods=['DELETE'])
@token_required
def delete_item(current_user, food_id):
    if current_user.id != 1:
        return jsonify({'message': 'Unauthorized access'}), 403

    item_to_delete = MonthlyMenu.query.get(food_id)

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

# Admin page route
@app.route('/admin-page', methods=['GET'])
@token_required
def admin_page(current_user):
    if current_user.id == 1:
        return jsonify({'message': 'Welcome to admin page'}), 200
    else:
        return jsonify({'message': 'Unauthorized access'}), 403

if _name_ == '_main_':
    app.