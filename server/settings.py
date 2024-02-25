from os import environ

# local
UPLOAD_PATH = "uploads"
MODEL_PATH = "best.pt"

# env
FLASK_PORT = environ.get("FLASK_PORT")
FIREBASE_KEY_PATH = environ.get("FIREBASE_KEY_PATH")
