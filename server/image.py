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

def run_inference(image: str) -> set[str]:
    '''
    run_inference returns a str[] that contains ingredient names
    and raw Image object that contains the original Image with 
    bounding boxes labeled  
    '''

    delete_upload = False
    if image.startswith("http"):
        image = upload_file_from_url(image)
        delete_upload = True
    
    model: YOLO = get_or_initialize_model()
    result = model.predict(f"{UPLOAD_PATH}/{image}")[0]
    boxes = result.boxes
    
    identified_item_names: set[str] = set()

    for box in boxes:
        if box.conf[0].item() >= 0.5: # Only add boxes that are more than 50% confident
            box_type_name: str = result.names(box.cls[0].item())
            identified_item_names.add(box_type_name)

    pil_image: Image = Image.fromarray(result.plot()[:, :, ::-1])

    image_jpeg_bytesIO: io.BytesIO = io.BytesIO()
    pil_image.save(image_jpeg_bytesIO, format="JPEG")
    
    if delete_upload:
        # delete the upload afterwards
        os.remove(f"{UPLOAD_PATH}/{image}")

    image_jpeg_bytes: bytes = image_jpeg_bytesIO.getvalue()

    f = open('../boxes/image_boxes.jpg', 'wb')
    f.write(image_jpeg_bytes)
    f.close()

    return identified_item_names

def scan_image(image: str):
    '''
    scan_image returns a str that represents text found in the
    image -- it does this by converting the image into grayscale
    and then collapses it into only two colors: black and white 
    '''
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

# util
def upload_file_from_url(url: str):
    image_data = requests.get(url).content
    filename = str(hash(url))

    if not os.path.exists(f"{UPLOAD_PATH}/{filename}"):
        with open(f"{UPLOAD_PATH}/{filename}", "wb") as file:
            file.write(image_data)
    
    return filename