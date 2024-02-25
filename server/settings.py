from os import environ

# local
UPLOAD_PATH = "uploads"
MODEL_PATH = "best.pt"

RECIPE_API_BASE = "https://foodcombo.com"
RECIPE_API_OPTIONS = "?returns=recipes&visible="

FOOD_SET = set()

with open("ingredients.txt", "r") as file:
    for line in file:
        FOOD_SET.add(line.strip().lower())

# env
FLASK_PORT = environ.get("FLASK_PORT")
FIREBASE_KEY_PATH = environ.get("FIREBASE_KEY_PATH")
