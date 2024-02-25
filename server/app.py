from flask import Flask
from dotenv import load_dotenv

import nutrition
from utils.firebase import FirebaseController

def init() -> Flask:
    load_dotenv()

    app = Flask(__name__)
    app.config.from_pyfile("settings.py", silent=True)
    
    app.register_blueprint(nutrition.bp)

    conn = FirebaseController(app.config.get("FIREBASE_KEY_PATH", ""))
    app.firebase = conn

    return app

if __name__ == "__main__":
    app = init()
    app.run(port=app.config.get("FLASK_PORT", 2000))