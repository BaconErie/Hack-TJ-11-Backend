from os import environ

FLASK_PORT = environ.get("FLASK_PORT")
# firebase-related and other secrets here
FIREBASE_URL = environ.get("FIREBASE_URL")