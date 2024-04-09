from flask import Flask, request, jsonify
from functools import wraps
from models import User, DailyMenu, Food, MonthlyMenu, Order, OrderItem  
import jwt
from auth import token_required
from flask import jsonify

@app.route('/user_details', methods=['GET'])
@token_required
def user_details(current_user):
    # Assuming current_user is the authenticated user object
    user_details = {
        'user_name': current_user.user_name,
        'wallet_balance': current_user.wallet
    }
    return jsonify({'user_details': user_details})

@app.route('/daily_menu', methods=['GET'])
@token_required
def daily_menu(current_user):
    food_details = []
    daily_menu_items = DailyMenu.query.all() # Assuming you have a way to fetch daily menu items
    for daily_menu in daily_menu_items:
        food = Food.query.get(daily_menu.food_id)
        food_dict = {
            'food_id': daily_menu.food_id,
            'item_name': food.item_name,
            'bought_count': food.bought_count,
            'price': food.price
        }
        food_details.append(food_dict)
    return jsonify({'daily_menu': food_details})

@app.route('/place_order', methods=['POST'])
@token_required
def place_order(current_user):
    # Get data from the request
    order_data = request.json
    order_items = order_data.get('items', [])

    # Calculate total amount based on order items
    total_amount = sum(item['quantity'] * item['total_price'] for item in order_items)

    # Increment the order token value
    last_order = Order.query.order_by(Order.order_id.desc()).first()
    token_value = 1 if last_order is None else last_order.token + 1

    # Check if wallet balance is sufficient
    if current_user.wallet < total_amount:
        return jsonify({'message': 'Insufficient balance'}), 400

    # Deduct total amount from wallet balance
    current_user.wallet -= total_amount

    # Create OrderItem instances and add them to the list of order items
    order_items_instances = []
    for item in order_items:
        food_id = item.get('food_id')
        quantity = item.get('quantity', 1)  # Default to 1 if quantity is not provided

        # Retrieve food details
        food = Food.query.get(food_id)
        if not food:
            return jsonify({'message': 'Food item not found'}), 404

        # Update bought count in Food table
        food.bought_count += quantity

        # Create an OrderItem and add it to the list of order items
        order_item = OrderItem(food_id=food_id, quantity=quantity, total_price=item['total_price'])
        order_items_instances.append(order_item)

    # Create the order
    order = Order(user_id=current_user.user_id, token=token_value, status='Delivered', total_amount=total_amount, items=order_items_instances)
    db.session.add(order)

    try:
        # Commit the changes to the database
        db.session.commit()
        # Return the token and order details with status "Delivered"
        return jsonify({'order_token': order.token, 'order_details': order_items, 'status': 'Delivered'}), 200
    except:
        # Rollback changes if an error occurs
        db.session.rollback()
        return jsonify({'message': 'Failed to place order. Please try again later.'}), 500


@app.route('/order_history', methods=['GET'])
@token_required
def get_combined_order_history(current_user):
    try:
        # Query for current orders ('Ordered' or 'Pinged')
        current_orders_subquery = db.session.query(
            Order.order_id, Order.order_date, Order.total_amount, Order.status,
            Order.token, # Include the token in the query
            db.literal_column("'Current'").label('order_type')
        ).filter(
            Order.user_id == current_user.user_id,
            Order.status.in_(['Ordered', 'Pinged'])
        ).subquery()

        # Query for past orders ('Delivered'), limiting to the last 5
        past_orders_subquery = db.session.query(
            Order.order_id, Order.order_date, Order.total_amount, Order.status,
            Order.token, # Include the token in the query
            db.literal_column("'Past'").label('order_type')
        ).filter(
            Order.user_id == current_user.user_id,
            Order.status == 'Delivered'
        ).order_by(
            Order.order_date.desc()
        ).limit(5).subquery()

        # Combine the results of both subqueries
        combined_orders = db.session.query(
            current_orders_subquery.c.order_id,
            current_orders_subquery.c.order_date,
            current_orders_subquery.c.total_amount,
            current_orders_subquery.c.status,
            current_orders_subquery.c.token, # Include the token in the combined query
            current_orders_subquery.c.order_type
        ).union_all(
            db.session.query(
                past_orders_subquery.c.order_id,
                past_orders_subquery.c.order_date,
                past_orders_subquery.c.total_amount,
                past_orders_subquery.c.status,
                past_orders_subquery.c.token, # Include the token in the combined query
                past_orders_subquery.c.order_type
            )
        ).all()

        # Serialize order data into JSON format
        order_history = []
        for order in combined_orders:
            order_data = {
                'order_id': order.order_id,
                'order_date': order.order_date.strftime('%Y-%m-%d %H:%M:%S'), # Convert datetime to string
                'total_amount': order.total_amount,
                'status': order.status,
                'order_type': order.order_type,
                'token': order.token # Include the token in the response
            }
            order_history.append(order_data)

        # Return the combined order history as a JSON response including the token
        return jsonify({'order_history': order_history}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch combined order history. Please try again later.', 'error': str(e)}), 500

