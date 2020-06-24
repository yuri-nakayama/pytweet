# initialize database and ORM for our database
# ORM: we used to automatically create database tables
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def init_db(app):
  db.init_app(app)
  Migrate(app, db)

  return db
