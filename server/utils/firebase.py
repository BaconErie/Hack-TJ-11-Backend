from firebase_admin import initialize_app, firestore, credentials
from firebase_functions.firestore_fn import DocumentSnapshot

from image import scan_image, run_inference

class FirebaseController():
    def __init__(self, firebase_key_path):
        self.creds = credentials.Certificate(firebase_key_path)
        self.app = initialize_app(self.creds)
        self.db = firestore.client()
        
        self.requests = self.db.collection("requests")
        self.outputs = self.db.collection("responses")

        self.requests.on_snapshot(self.listen_to_status)

    def add_document(self, collection: str, value: dict):
        if collection.lower() == "requests":
            doc = self.requests.document()
        elif collection.lower() == "outputs":
            doc = self.outputs.document()

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
        value = dict()

        match task:
            case "ocr":
                link: str = doc.get("link")
                text: str = scan_image(link)
                value = {
                    "result": text
                }
            case "ingredients":
                # run model inference
                link: str = doc.get("link")
                result = run_inference(link)  
                value = {
                    "result": result
                } 

        self.add_document("outputs", value)