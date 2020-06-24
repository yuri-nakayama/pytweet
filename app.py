# pip3 install -r requirements.txt
# registers DB to Flask
from flask import Flask
from .database import init_db
from .config import Config
import os
import pytweet.models # this is for making the table of database

# after is initializes db and ORM, it will go into app.py and connect to FLASK in order to connect us into models.py

def create_app():
  app = Flask(__name__) # creating an instance of Flask
  app.config.from_object(Config) # passing the Config object to Flask
  app.secret_key = os.urandom(24) # this is for generating secret keys that will display 24 strings
  init_db(app) # passing the flask object into our init_db() database connection

  return app

app = create_app() # calling the create_app() function