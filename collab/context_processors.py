
from django.conf import settings


def custom_contexts(request):
    return {
        'APPLICATION_NAME': settings.APPLICATION_NAME,
        'LOGO_PATH': settings.LOGO_PATH,
        'APPLICATION_ABSTRACT': settings.APPLICATION_ABSTRACT,
        'IMAGE_FORMAT': settings.IMAGE_FORMAT,
        'FILE_MAX_SIZE': settings.FILE_MAX_SIZE,
    }
