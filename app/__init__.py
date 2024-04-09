from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from .extensions import db
from flask_bcrypt import Bcrypt


def create_app():
  app = Flask(__name__)
  app.config['SECRET_KEY'] = 'some random string'
  app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///database.db'
  db.init_app(app)
  bcrypt = Bcrypt(app)


  from .models import Admin,User,Food,MonthlyMenu,DailyMenu,Order

  create_database(app)
  
  return app

def create_database(app):
  with app.app_context():
    if not path.exists('website/'+ 'database.db'):
      db.create_all()
      print('Create Database!')




