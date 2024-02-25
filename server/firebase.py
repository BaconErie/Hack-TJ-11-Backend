from firebase_admin import initialize_app, firestore, credentials
from firebase_functions.firestore_fn import DocumentSnapshot, DocumentReference

from image import scan_image, run_inference
from nutrition import harris_benedict

class FirebaseController():
    def __init__(self, firebase_key_path):
        self.creds = credentials.Certificate(firebase_key_path)
        self.app = initialize_app(self.creds)
        self.db = firestore.client()
        
        self.requests = self.db.collection("requests")
        self.outputs = self.db.collection("responses")
        self.ingredients = self.db.collection("ingredients")
        self.users = self.db.collection("users")

        self.requests.on_snapshot(self.listen_to_status)

    def add_document(self, collection: str, value: dict):
        if collection.lower() == "requests":
            doc = self.requests.document()
        elif collection.lower() == "outputs":
            doc = self.outputs.document()
        elif collection.lower() == "ingredients":
            doc = self.ingredients.document()

        doc.set(value)
    
    def listen_to_status(self, *args) -> None:
        for doc in args[0]:
            status = doc.get("status")
            
            match status:
                case "dead":
                    doc.reference.delete()
                case "pending":
                    doc.reference.update({"status": "running"})
                case "running":
                    self.run_task(doc)
                    doc.reference.set({"status": "dead"})

    def run_task(self, doc: DocumentSnapshot):
        task = doc.get("task")
        
        match task:
            case "ocr":
                link: str = doc.get("link")
                text: str = scan_image(link)
                
                value: dict = {
                    "result": text
                }
            case "ingredients":
                link: str = doc.get("link")
                result: set[str] = run_inference(link)  
                ingredients: set[str] = result

                for ingredient in ingredients:
                    value: dict = {
                        "name": ingredient
                    }

                    self.add_documents("ingredients", value)
                
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
                elif goal == "lose":
                    bmr -= bmr*0.15
                
                udict["dailycalories"] = bmr
                udoc.update(udict)             
            case "calories":
                pass