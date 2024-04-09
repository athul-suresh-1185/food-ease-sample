from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

# Assuming db is initialized in your models.py file
# from .models import db, Food

DB_NAME = 'database.db'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'some random string'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    # Initialize db with the app
    db.init_app(app)

    # Import models after initializing db
    from .models import Admin, User, Food, MonthlyMenu, DailyMenu, Order

    # Ensure the database is created
    create_database(app)

    return app

def create_database(app):
    with app.app_context():
        if not path.exists('website/' + DB_NAME):
            db.create_all()
            print('Database created!')

# Ensure db is initialized in your models.py file
# db = SQLAlchemy()

