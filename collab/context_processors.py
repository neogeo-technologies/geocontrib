from django.conf import settings
from collab.models import Authorization

import logging

logger = logging.getLogger('django')


def custom_contexts(request):
    try:
        user_level_projects = Authorization.get_user_level_projects(request.user)
    except Exception:
        user_level_projects = {}
        logger.exception('Cannot retrieve user level project')

    return {
        'APPLICATION_NAME': settings.APPLICATION_NAME,
        'LOGO_PATH': settings.LOGO_PATH,
        'APPLICATION_ABSTRACT': settings.APPLICATION_ABSTRACT,
        'IMAGE_FORMAT': settings.IMAGE_FORMAT,
        'FILE_MAX_SIZE': settings.FILE_MAX_SIZE,
        'USER_LEVEL_PROJECTS': user_level_projects
    }
