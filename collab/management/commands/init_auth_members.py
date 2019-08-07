from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from collab.models import Authorization
from collab.models import Project
from collab.models import UserLevelPermission

import logging

logger = logging.getLogger('django')
User = get_user_model()


class Command(BaseCommand):
    help = """Permet de donner un role à tous les utilisateurs pour tous les projets"""

    def handle(self, *args, **options):
        connected = UserLevelPermission.objects.get(rank=1)
        for user in User.objects.filter(is_active=True):
            for project in Project.objects.all():
                auth, created = Authorization.objects.get_or_create(
                    project=project,
                    user=user,
                    defaults={'level': connected}
                )
                if created:
                    logger.info("user {} added to {}".format(user.username, project.title))

        logger.info('Tasks succeessed! ')
