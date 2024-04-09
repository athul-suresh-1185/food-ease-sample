from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from .models import db, Food

db = SQLAlchemy()
DB_NAME = 'database.db'


def create_app():
  app = Flask(__name__)
  app.config['SECRET_KEY'] = 'some random string'
  app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
  db.init_app(app)


  from .models import Admin,User,Food,MonthlyMenu,DailyMenu,Order

  create_database(app)
  
  return app

def create_database(app):
  with app.app_context():
    if not path.exists('website/'+ DB_NAME):
      db.create_all()
      add_dummy_food_data()
      create_dummy_admins()
      create_dummy_users()
      print('Create Database!')

def add_dummy_food_data():
  # Sample food items
  food_items = [
      Food(item_name='Pizza', bought_count=0, price=10.99),
      Food(item_name='Burger', bought_count=0, price=8.99),
      Food(item_name='Salad', bought_count=0, price=7.99),
      # Add more food items as needed
  ]

  # Add food items to the session
  for food in food_items:
      db.session.add(food)

  # Commit the changes
  db.session.commit()


def create_dummy_users():
  # Sample users
  users = [
      User(user_name='John Doe', password='password123', wallet=1000.00),
      User(user_name='Jane Smith', password='password456', wallet=2000.00),
      User(user_name='Alice Johnson', password='password789', wallet=3000.00),
  ]

  # Add users to the session
  for user in users:
      db.session.add(user)

  # Commit the changes
  db.session.commit()

def create_dummy_admins():
  # Sample admins
  admins = [
      Admin(user_name='Admin1', password='admin123'),
      Admin(user_name='Admin2', password='admin456'),
  ]

  # Add admins to the session
  for admin in admins:
      db.session.add(admin)

  # Commit the changes
  db.session.commit()


