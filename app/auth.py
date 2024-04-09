from flask import Flask, request, jsonify
from functools import wraps
from models import User, DailyMenu  
import jwt


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

@app.route('/user-login', methods=['POST'])
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