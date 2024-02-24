from flask import Blueprint
from ml.model import get_or_initialize_model

bp = Blueprint("image", __name__, url_prefix="/image")

bp.route("/request", methods=["POST"])
def request_inference():
    pass

def run_inference():
    model = get_or_initialize_model()
    pass

# other image related methods here