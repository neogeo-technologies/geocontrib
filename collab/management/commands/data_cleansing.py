from django.core.management.base import BaseCommand
from django.utils import timezone

from collab.models import Feature

import logging

logger = logging.getLogger('django')


class Command(BaseCommand):
    help = """Commande pouvant etre associé à une tâche CRON,
        qui supprime et/ou archive les signalments arrivant à termes."""

    def add_arguments(self, parser):
        parser.add_argument(
            dest='task_name', type=str, choices=['all', 'delete_feature', 'archive_feature'],
            help="""Nom de la tache à executer et à choisir parmi:
                'all', 'delete_feature', 'archive_feature' """
        )

    def delete_feature(self):
        features = Feature.objects.filter(deletion_on__lte=timezone.now())
        nb_features = features.count()
        for feature in features:
            feature.delete()
        logger.info('NB deleted features: {}'.format(nb_features))

    def archive_feature(self):
        features = Feature.objects.filter(archived_on__lte=timezone.now())
        nb_features = features.count()
        for feature in features:
            feature.status = 'archived'
            feature.save()
        logger.info('NB archived features: {}'.format(nb_features))

    def handle(self, *args, **options):
        tasks = options['task_name']
        if 'all' not in tasks:
            if 'delete_feature' in tasks:
                self.delete_feature()
            if 'archive_feature' in tasks:
                self.archive_feature()
        else:
            self.delete_feature()
            self.archive_feature()

        logger.info('Tasks succeessed! ')
