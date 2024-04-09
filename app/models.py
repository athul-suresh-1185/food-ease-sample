from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Admin(db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    wallet = db.Column(db.Float, nullable=False)

class Food(db.Model):
    __tablename__ = 'food'
    food_id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    bought_count = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

class MonthlyMenu(db.Model):
    __tablename__ = 'monthly_menu'
    food_id = db.Column(db.Integer, db.ForeignKey('food.food_id'), primary_key=True)
    food = db.relationship('Food', backref=db.backref('monthly_menu', lazy=True))

class DailyMenu(db.Model):
    __tablename__ = 'daily_menu'
    food_id = db.Column(db.Integer, db.ForeignKey('food.food_id'), primary_key=True)
    food = db.relationship('Food', backref=db.backref('daily_menu', lazy=True))

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey('food.food_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    token = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    items = db.relationship('OrderItem', backref='order', lazy=True)
    status = db.Column(db.String(50), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)