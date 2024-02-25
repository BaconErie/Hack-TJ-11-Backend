import requests
from firebase_admin import initialize_app, firestore, credentials
from firebase_functions.firestore_fn import DocumentSnapshot, DocumentReference

from image import scan_image, run_inference
from nutrition import harris_benedict
from settings import RECIPE_API_BASE, RECIPE_API_OPTIONS

class FirebaseController():
    def __init__(self, firebase_key_path):
        self.creds = credentials.Certificate(firebase_key_path)
        self.app = initialize_app(self.creds)
        self.db = firestore.client()
        
        self.requests = self.db.collection("requests")
        self.outputs = self.db.collection("responses")
        self.users = self.db.collection("users")

        self.requests.on_snapshot(self.listen_to_status)

    def add_document(self, collection: str, value: dict, user: DocumentReference=None):
        if collection.lower() == "requests":
            doc = self.requests.document()
        elif collection.lower() == "outputs":
            doc = self.outputs.document()
        elif collection.lower() == "ingredients":
            doc = user.collection("ingredients").document()
        elif collection.lower() == "recipes":
            doc = user.collection("recipes").document()

        doc.set(value)
    
    def listen_to_status(self, *args) -> None:
        for doc in args[0]:
            status = doc.get("status")
            
            match status:
                case "dead":
                    doc.reference.delete()
                case "pending":
                    ref = doc.to_dict()
                    ref["status"] = "running"
                    doc.reference.update(ref)
                case "running":
                    self.run_task(doc)
                    doc.reference.set({"status": "dead"})

    def run_task(self, doc: DocumentSnapshot):
        task = doc.get("task")
        
        match task:
            case "receipt":
                id = doc.get("item")
                link: str = doc.get("link")
                words: set[str] = scan_image(link)
                udoc: DocumentReference = self.users.document(id)

                for word in words:
                    value: dict = {
                        "name": word
                    }

                    self.add_document("ingredients", value, udoc)
                
                self.generate_recipes(udoc, words)
            case "ingredients":
                id = doc.get("item")
                link: str = doc.get("link")
                ingredients: set[str] = run_inference(link)
                udoc: DocumentReference = self.users.document(id)

                for ingredient in ingredients:
                    value: dict = {
                        "name": ingredient
                    }
                    
                    self.add_document("ingredients", value, udoc)
                
                self.generate_recipes(udoc, ingredients)
            case "bmr":
                id = doc.get("item")
                udoc: DocumentReference = self.users.document(id)
                user: DocumentSnapshot = udoc.get()
                udict: dict = user.to_dict()
                
                weight = user.get("weight") # pounds
                age = user.get("age") # years
                height = user.get("height") # inches
                sex = user.get("sex").lower() # female | male
                activity = user.get("activity").lower() # low | medium | high 
                goal = user.get("goal").lower().split(" ")[0] # gain weight | maintain weight | lose weight

                bmr = harris_benedict(age, weight, height, sex, activity)

                if goal == "gain":
                    bmr += bmr*0.15
                    bmr = int(bmr)
                elif goal == "lose":
                    bmr -= bmr*0.15
                    bmr = int(bmr)

                try:
                    calories = user.get("calories")
                except:
                    calories = 0
                    udict["calories"] = 0
                progress: float = (1.0*calories)/(1.0*bmr)

                # fit to [0,1]
                if progress > 1: 
                    progress = 1
                elif progress < 0:
                    progress = 0

                udict["dailycalories"] = bmr
                udict["progress"] = progress
                udoc.update(udict)
            case "recipe":
                id = doc.get("item")
                udoc: DocumentReference = self.users.document(id)
                try:
                    amount = doc.get("amount")
                except:
                    amount = 3

                docs: list[DocumentSnapshot] = udoc.collection("ingredients").get()
                ingredients: set[str] = set()

                for ingredient in docs:
                    ingredients.add(ingredient.get("name"))
                
                self.generate_recipes(udoc, ingredients, amount)
            case "calories":
                id = doc.get("item")
                add_cals = int(doc.get("addcalories"))
                udoc: DocumentReference = self.users.document(id)
                user: DocumentSnapshot = udoc.get()
                udict: dict = user.to_dict()
                
                try:
                    calories = user.get("calories")
                except:
                    calories = 0
                    udict["calories"] = 0
                udict["calories"] = calories+add_cals
                calories = udict["calories"]
                progress: float = (1.0*calories)/(1.0*udict["dailycalories"])

                # fit to [0,1]
                if progress > 1: 
                    progress = 1
                elif progress < 0:
                    progress = 0

                udict["progress"] = progress
                udoc.update(udict)
    
    def generate_recipes(self, udoc: DocumentReference, ingredients: set[str], amount=3):
        old_recipes: list[DocumentSnapshot] = udoc.collection("recipes").get()
        for recipe in old_recipes:
            recipe.reference.delete()

        plural_dict = {
            'apple': 'apples',
            'banana': 'bananas',
            'beet': 'beets',
            'carrot': 'carrots',
            'cucumber': 'cucumbers',
            'egg': 'eggs',
            'eggplant': 'eggplants',
            'onion': 'onions',
            'potato': 'potatoes',
            'tomato': 'tomatoes',
            'orange': 'orange'
        }

        new_ingredients = []
        for ingredient in ingredients:
            if ingredient in plural_dict.keys():
                new_ingredients.append(plural_dict[ingredient])
            else:
                new_ingredients.append(ingredient)
        
        ingredients = new_ingredients

        recipe_path = "/".join(ingredients)
        recipe_url = f"{RECIPE_API_BASE}/api/recipes/{recipe_path}{RECIPE_API_OPTIONS}{amount}"

        response = requests.get(recipe_url, headers={"Referer": f"{RECIPE_API_BASE}"})
        response = response.json()
        
        for info in response["recipes"]:
            recipe_id = info["id"]
            calorie_url = f"{RECIPE_API_BASE}/api/recipe/info/{recipe_id}"
                
            recipe_response = requests.get(calorie_url, headers={"Referer": f"{RECIPE_API_BASE}"})
            recipe_response = recipe_response.json()

            calorie_count = int(float(recipe_response["recipe"]["nutrients"]["calories"]))

            value = {
                "name": info["title"],
                "url": info["url"],
                "calories": calorie_count
            }
            
            self.add_document("recipes", value, udoc)
        
        if len(response["recipes"]) == 0:
            self.add_document("recipes", {"name": "No recipes found", "url": "", "calories": 0}, udoc)
