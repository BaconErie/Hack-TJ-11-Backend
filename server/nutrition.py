def calculate_bmr(age: int, height: int, weight: int, sex: str) -> float:
    '''
    calculate_bmr returns an float that represents the
    BMR of the user -- age must be of type int in years, 
    height must be of type int in inches, weight must be of
    type in pounds, and sex must be of type "female" | "male"
    '''
    sex = sex.lower().strip()

    if sex == "female":
        return ((4.7 * height +
                4.35 * weight) - 
                4.7 * age) + 655
    else:
        return ((12.7 * height +
                 6.23 * weight) -
                 6.8 * age) + 66
    
def harris_benedict(age: int, height: int, weight: int, sex: str, activity: str) -> float:
    '''
    harris_benedict returns a float that represents the 
    result of the Harris Benedict equation by using the
    BMR of the user 
    '''
    bmr = calculate_bmr(age, height, weight, sex)

    match activity:
        case "low":
            bmr *= 1.2
        case "medium":
            bmr *= 1.55 
        case "high":
            bmr *= 1.725
    
    return bmr