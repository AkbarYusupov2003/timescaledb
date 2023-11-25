import jwt


def get_group_by_age(age):
    if age <= 6:
        return 0
    elif age <= 12:
        return 1
    elif age <= 16:
        return 2
    elif age <= 18:
        return 3
    elif age <= 21:
        return 4
    elif age <= 28:
        return 5
    elif age <= 36:
        return 6
    elif age <= 46:
        return 7
    elif age <= 54:
        return 8
    else:
        return 9


def get_data_from_token(token):
    try:
        data = jwt.decode(token, options={"verify_signature": False})
        return data
    except Exception as e:
        print("Exception", e)
        return "" # Exception({"error": "token validation"})
