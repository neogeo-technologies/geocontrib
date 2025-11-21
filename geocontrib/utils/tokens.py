from django.core import signing
from django.conf import settings
from django.utils.crypto import get_random_string

def generate_subscribe_token(user, project):
    payload = {
        "u": user.id,
        "p": project.id,
        "nonce": get_random_string(12)  # usage unique
    }
    return signing.dumps(payload, key=settings.SECRET_KEY)

def validate_subscribe_token(token):
    try:
        data = signing.loads(token, key=settings.SECRET_KEY)
        return data
    except signing.BadSignature:
        return None
