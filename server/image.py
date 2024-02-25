import requests
import os 
import cv2
from ultralytics import YOLO
from functools import cache
from pytesseract import image_to_string
from PIL import Image
import io

from settings import UPLOAD_PATH, MODEL_PATH

@cache
def get_or_initialize_model() -> YOLO:
    model = YOLO(MODEL_PATH)
    return model

def run_inference(image: str) -> list[str]:
    '''Returns an array with string that has the food names. 
    Also puts the boxed image into the database.
    Each item in the list is unique; you will not find, for example, two apple strings in the return'''

    delete_upload = False
    if image.startswith("http"):
        image = upload_file_from_url(image)
        delete_upload = True
    
    model: YOLO = get_or_initialize_model()
    result = model.predict(f"{UPLOAD_PATH}/{image}")[0] # To be used by the o
    boxes = result.boxes
    
    identified_item_names: str = []

    for box in boxes:
        box_type_name: str = result.names(box.cls[0].item())

        if not box_type_name in identified_item_names:
            identified_item_names.append(box_type_name)

    pil_image: Image = Image.fromarray(result.plot()[:, :, ::-1])

    image_jpeg_bytes = io.BytesIO()
    pil_image.save(image_jpeg_bytes, format="JPEG")

    if delete_upload:
        # delete the upload afterwards
        os.remove(f"{UPLOAD_PATH}/{image}")

    return identified_item_names

def scan_image(image: str):
    delete_upload = False
    if image.startswith("http"):
        image = upload_file_from_url(image)
        delete_upload = True
    
    img: cv2.Mat = cv2.imread(f"{UPLOAD_PATH}/{image}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    text = image_to_string(img, lang="eng")

    if delete_upload:
        # delete the upload afterwards
        os.remove(f"{UPLOAD_PATH}/{image}")

    return text

def upload_file_from_url(url: str):
    image_data = requests.get(url).content
    filename = str(hash(url))

    if not os.path.exists(f"{UPLOAD_PATH}/{filename}"):
        with open(f"{UPLOAD_PATH}/{filename}", "wb") as file:
            file.write(image_data)
    
    return filename