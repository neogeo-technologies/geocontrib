from uuid import uuid4, UUID
import csv
import logging

from django.contrib.gis.geos import GEOSGeometry, Point
from django.contrib.gis.geos.error import GEOSException
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from geocontrib.models import Feature
from geocontrib.models import FeatureLink

logger = logging.getLogger(__name__)

class CSVProcessingFailed(Exception):
    pass


class CSVProcessing:

    def __init__(self, *args, **kwargs):
        self.infos = []

    def get_geom(self, lon, lat):
        geom = Point(float(lon), float(lat))
        try:
            geom = GEOSGeometry(geom, srid=4326)
        except (GEOSException, ValueError):
            geom = None
        return geom

    def get_feature_data(self, feature_type, properties, field_names):
        feature_data = {}
        if hasattr(feature_type, 'customfield_set'):
            for field in field_names:
                feature_data[field] = properties.get(field)
        return feature_data

    def validate_uuid4(self, id):
        try:
            val = UUID(id, version=4)
        except ValueError:
            # If it's a value error, then the string 
            # is not a valid hex code for a UUID.
            return False

        return True

    def handle_title(self, title, feature_id):
        if not feature_id or feature_id == '' or (feature_id and not self.validate_uuid4(feature_id)):
            uid = uuid4()
            feature_id = str(uid)
        if not title or title == '':
            title = feature_id
            if not feature_id or feature_id == '':
                title = feature_id
        return title, feature_id

    @transaction.atomic
    def create_features(self, import_task):
        with open(import_task.file.path, 'r') as csvfile:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(csvfile.read())
            csvfile.seek(0)
            data = csv.DictReader(csvfile, dialect=dialect)
            features = list(data)
            if len(features) == 0:
                self.infos.append(
                    "Aucun signalement n'est indiqué dans l'entrée 'features'. ")
                raise CSVProcessingFailed
  
            feature_type = import_task.feature_type
            nb_features = len(features)
            field_names = feature_type.customfield_set.values_list('name', flat=True)
        
            for feature in features:
                feature_data = self.get_feature_data(
                    feature_type, feature, field_names)
                feature_title = feature.get("title")
                id = feature.get("id")
                title, feature_id = self.handle_title(feature_title, id)
                description = feature.get('description')
                status = feature.get('status', 'draft')
        
                if status not in [choice[0] for choice in Feature.STATUS_CHOICES]:
                    logger.warn("Feature '%s' import: status '%s' unknown, defaulting to 'draft'",
                                title, status)
                    status = "draft"
        
                try:
                    try:
                        feature_exist = Feature.objects.get(feature_id=feature_id)
                    except Feature.DoesNotExist:
                        feature_exist = None
                        # Le geojson peut venir avec un ancien ID. On reset l'ID ici aussi
                        feature_id = None
                   
                    if feature_exist:
                        if feature_exist.project != feature_type.project or feature_exist.feature_type != feature_type:
                            # Si l'ID qui vient du geojson de l'import existe, 
                            # mais on souhaite créer le signalement dans un autre projet
                            # On set l'ID à None
                            feature_id = None
                    current, _ = Feature.objects.update_or_create(
                        feature_id=feature_id,
                        # project=feature_type.project,
                        defaults={
                            'title': title,
                            'description' : description,
                            # TODO fix status
                            'status': status,
                            'creator': import_task.user,
                            'project' : feature_type.project,
                            'feature_type' : feature_type,
                            'geom' : self.get_geom(feature.get('lon'), feature.get('lat')),
                            'feature_data' : feature_data,
                        }
                    )
                    
                except Exception as er:
                    logger.exception(
                        f"L'edition de feature a echoué {er}'. ")
                    self.infos.append(
                        f"L'edition de feature a echoué {er}'. ")
                    raise CSVProcessingFailed  
        
                if title:
                    simili_features = Feature.objects.filter(
                        Q(title=title, description=description, feature_type=feature_type) | Q(
                            geom=current.geom, feature_type=feature_type)
                    ).exclude(feature_id=current.feature_id)
                    if simili_features.exists():
                        for row in simili_features:
                            FeatureLink.objects.get_or_create(
                                relation_type='doublon',
                                feature_from=current,
                                feature_to=row
                            )
        
            if nb_features > 0:
                msg = "{nb} signalement(s) importé(s). ".format(nb=nb_features)
                self.infos.append(msg)

    def validate_data(self, file):
        try:
            with open(file.path, 'r') as csvfile:
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(csvfile)
                data = csv.DictReader(csvfile, delimiter=dialect.delimiter)
        except Exception as err:
            logger.warn(type(err), err)
            self.infos.append(
                "Erreur à la lecture du fichier CSV: {} ".format(str(err)))
            raise CSVProcessingFailed
        else:
            return data

    def __call__(self, import_task):
        try:
            import_task.status = "processing"
            import_task.started_on = timezone.now()
            self.create_features(import_task)
        except CSVProcessingFailed as err:
            logger.warn('%s' % type(err))
            import_task.status = "failed"
        else:
            import_task.status = "finished"
            import_task.finished_on = timezone.now()
        import_task.infos = "/n".join(self.infos)
        import_task.save(update_fields=['status', 'started_on', 'finished_on', 'infos'])


def csv_processing(import_task):
    process = CSVProcessing()
    process(import_task)
