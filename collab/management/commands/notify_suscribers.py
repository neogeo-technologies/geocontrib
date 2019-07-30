from django.core.management.base import BaseCommand

import logging
logger = logging.getLogger('django')


class Command(BaseCommand):
    help = """Commande pouvant etre associé à une tache CRON et notifiant les utilisateurs,
        des evenements les concernant."""

    def notify_subscribers(self):
        """Définir les modalité de notification et d'abonnement"""
        pass

    def handle(self, *args, **options):
        self.notify_subscribers()
        logger.info('Command succeded! ')
