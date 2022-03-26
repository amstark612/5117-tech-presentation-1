from dotenv import load_dotenv, find_dotenv
from flask import Flask
from os import environ as env
from models import db

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://nuboigmmknakzz:a7d342e7b0206040e87b2b389ef905fa48c6a02e7358254143a38f3827a968a0@ec2-3-227-195-74.compute-1.amazonaws.com:5432/d2du69hn3mo0mh'

    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        db.init_app(app)

    return app
