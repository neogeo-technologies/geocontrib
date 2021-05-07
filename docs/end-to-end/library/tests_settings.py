from decouple import config

PARAMS = [
    "URL",
    "ADMINURL",
    "SUPERUSERNAME",
    "SUPERUSERPASSWORD",
]

def get_variables():
    variables = dict()

    for param in PARAMS:
        variables[param] = config(param)

    return variables
