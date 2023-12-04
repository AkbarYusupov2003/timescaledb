import jwt


ALLOWED_PERIODS = ("hours", "day", "month")
TRANSLATE_ALLOWED_PERIODS = {"day": "За этот день", "month": "За этот месяц", "hours": "За этот час"}

AGE_GROUP_DICT = {
    "0": "0-6",
    "1": "7-12",
    "2": "13-15",
    "3": "16-18",
    "4": "19-21",
    "5": "22-28",
    "6": "29-36",
    "7": "37-46",
    "8": "47-54",
    "9": "55+",
}



CHILDREN_AGE_GROUPS = ("0", "1", "2")

def get_group_by_age(age):
    if age <= 6:
        return 0
    elif age <= 12:
        return 1
    elif age <= 15:
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
        return None
