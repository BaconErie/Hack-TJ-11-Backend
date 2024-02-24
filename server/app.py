from flask import Flask
from dotenv import load_dotenv

import image

def init() -> Flask:
    load_dotenv()

    app = Flask(__name__)
    app.config.from_pyfile("settings.py", silent=True)
    
    app.register_blueprint(image.bp)

    return app

if __name__ == "__main__":
    app = init()
    app.run(port=app.config.get("FLASK_PORT", 2000))