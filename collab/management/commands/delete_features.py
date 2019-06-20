from collab import models
import datetime
from django.core.management.base import BaseCommand
from collab.views.services.deletion_archive_services import delete_all_features

APP_NAME = __package__.split('.')[0]


class Command(BaseCommand):
    help = 'Cette fonction permet de supprimer des signalements'

    def handle(self, *args, **options):

        for feature_type in models.FeatureType.objects.all():

            project = feature_type.project_set.all()
            if project:
                project_slug = project[0].slug
                # from datetime import date, time, datetime
                # deletion_date = date(2050, 1, 1)
                deletion_date = datetime.datetime.now().date()
                feature_slug = feature_type.feature_type_slug
                if deletion_date:
                    list_ids = delete_all_features(APP_NAME, project_slug,
                                                   feature_slug, deletion_date)


        self.stdout.write(self.style.SUCCESS('FIN DU TRAITEMENT DE SUPPRESSION DES SIGNALEMENTS.'))
