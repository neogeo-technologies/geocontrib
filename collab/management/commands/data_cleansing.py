from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from collab.models import Feature
from collab.models import Event

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
        features = Feature.objects.exclude(status='draft').filter(deletion_on__lte=timezone.now())
        nb_features = features.count()
        for feature in features:
            Event.objects.create(
                feature_id=feature.feature_id,
                event_type='delete',
                object_type='feature',
                user=feature.creator,
                project_slug=feature.project.slug,
                feature_type_slug=feature.feature_type.slug,
                data=feature.feature_data
            )
            feature.delete()
        logger.info('NB deleted features: {}'.format(nb_features))

    def archive_feature(self):

        features = Feature.objects.exclude(Q(status='draft') | Q(status='archived')).filter(archived_on__lte=timezone.now())
        nb_features = features.count()
        for feature in features:
            feature.status = 'archived'
            feature.save()
            Event.objects.create(
                feature_id=feature.feature_id,
                event_type='archive',
                object_type='feature',
                user=feature.creator,
                project_slug=feature.project.slug,
                feature_type_slug=feature.feature_type.slug,
                data=feature.feature_data
            )
            logger.info('Feature {0} archived'.format(feature.feature_id))
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
