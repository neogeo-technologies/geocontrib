from collab import models
import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from collab.views.services.feature_services import archive_all_features

APP_NAME = __package__.split('.')[0]


class Command(BaseCommand):
    help = "Cette fonction permet d'archiver des signalements"

    def handle(self, *args, **options):

        for feature_type in models.FeatureType.objects.all():

            project = feature_type.project_set.all()
            if project:
                project_slug = project[0].slug
                # from datetime import date
                # archive_date = date(2050, 1, 1)
                archive_date = datetime.datetime.now().date()
                feature_slug = feature_type.feature_type_slug
                list_ids = archive_all_features(APP_NAME, project_slug,
                                                feature_slug, archive_date)


        self.stdout.write(self.style.SUCCESS('FIN DU TRAITEMENT D ARCHIVAGE DES SIGNALEMENTS.'))
