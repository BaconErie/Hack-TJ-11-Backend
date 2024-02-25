from flask import Blueprint, jsonify

bp = Blueprint("nutrition", __name__, url_prefix="/nutrition")

def calculate_bmr(age: int, height: int, weight: int, sex: str) -> int:
    height = height * 2.5
    sex = sex.lower().trim()

    if sex == "female":
        return ((4.7 * height +
                4.35 * weight) - 
                4.7 * age) + 655
    else:
        return ((12.7 * height +
                 6.23 * weight) -
                 6.8 * age) + 66

@bp.route("/bmr/<age>/<height>/<weight>/<sex>")
def bmr(age, height, weight, sex):
    response = {}
    
    try:
        age = int(age)
        height = int(height)
        weight = int(weight)
        sex = str(sex) 
        
        if not sex: #moment ok dude
            response["success"] = False
            response["message"] = "Missing value: 'sex'"
            return jsonify(response)
    except: 
        response["success"] = False
        response["message"] = "An unexpected error occurred!"
        return jsonify(response)

    bmr = calculate_bmr(age, height, weight, sex)
    
    response["success"] = True
    response["result"] = bmr
    
    return jsonify(response)