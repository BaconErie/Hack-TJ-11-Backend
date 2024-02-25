from flask import Flask
from dotenv import load_dotenv

from firebase import FirebaseController

def init() -> Flask:
    load_dotenv()

    app = Flask(__name__)
    app.config.from_pyfile("settings.py", silent=True)
    
    controller = FirebaseController(app.config.get("FIREBASE_KEY_PATH", ""))
    app.firebase = controller

    return app

if __name__ == "__main__":
    app = init()
    app.run(port=app.config.get("FLASK_PORT", 2000))