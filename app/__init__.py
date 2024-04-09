from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from .models import db, Food
from app import db 

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
      print('Create Database!')




