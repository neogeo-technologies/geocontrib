from collab import models
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Cette fonction permet de supprimer des signalements'

    def handle(self, *args, **options):

        for feature_type in models.FeatureType.objects.all():
            # import pdb; pdb.set_trace()
            project = feature_type.project_set.all()
            if project:
                project_slug = project[0].slug
                feature_slug = feature_type.feature_type_slug



        self.stdout.write(self.style.SUCCESS('FIN DU TRAITEMENT DE SUPPRESSION DES SIGNALEMENTS.'))
