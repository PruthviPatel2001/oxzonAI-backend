from flask_pymongo import PyMongo

mongo = PyMongo()  # Initialize without the app

def init_app(app):
    mongo.init_app(app)  # Now bind it to the app
