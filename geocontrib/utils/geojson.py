from uuid import uuid4
import json
import logging

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos.error import GEOSException
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from geocontrib.models import Feature
from geocontrib.models import FeatureLink

logger = logging.getLogger(__name__)

# Custom exception class for handling failures in GeoJSON processing
class GeoJSONProcessingFailed(Exception):
    pass

# Class for processing GeoJSON and JSON data
class GeoJSONProcessing:
    """
    This class is designed to process both GeoJSON and JSON data formats. It can handle scenarios
    where features do not have geographical data ('geom'), following an update to support non-geographical
    feature types. The class provides methods to validate, create, and check features, adapting to the presence
    or absence of geometry data.

    GeoJSON vs. JSON Handling:
    The class discerns between GeoJSON and JSON formats based on the structure of the input data.
    For GeoJSON, it expects a dictionary format with a 'features' key. For JSON format, typically
    used for non-geographical data, it accepts a list of features.

    Feature Creation and Validation:
    The class includes methods to create feature instances in the database, validate input data, and handle
    specific attribute processing like generating titles and extracting custom field data.
    """

    def __init__(self, *args, **kwargs):
        self.infos = []  # Information messages to be logged or displayed

    def get_geom(self, geom):
        # If geoJSON, converts GeoJSON geometry to GEOSGeometry object, or returns None if conversion fails
        if isinstance(geom, dict):
            geom = str(geom)
        try:
            geom = GEOSGeometry(geom, srid=4326)
        except (GEOSException, ValueError):
            geom = None
        return geom

    def get_feature_data(self, feature_type, properties, field_names):
        # Extracts and returns custom field data from properties based on the feature type
        feature_data = {}
        if hasattr(feature_type, 'customfield_set'):
            for field in field_names:
                feature_data[field] = properties.get(field)
        return feature_data

    def handle_title(self, title, feature_id):
        # Handles title generation based on feature_id, generates UUID if both are missing
        if not title or title == '':
            title = feature_id
            if not feature_id or feature_id == '':
                uid = uuid4()
                feature_id = str(uid)
                title = feature_id

        return title, feature_id

    @transaction.atomic
    def create_features(self, features, import_task):
        # Creates Feature instances from provided features list
        feature_type = import_task.feature_type
        nb_features = len(features)
        field_names = feature_type.customfield_set.values_list('name', flat=True)

        for feature in features:
            properties = feature.get('properties', feature) # TODO : add fallback with feature for json

            feature_data = self.get_feature_data(
                feature_type, properties, field_names)

            title, feature_id = self.handle_title(
                properties.get("title"), feature.get("id"))

            description = properties.get('description')

            status = properties.get('status', 'draft')
            if status not in [choice[0] for choice in Feature.STATUS_CHOICES]:
                logger.warn("Feature '%s' import: status '%s' unknown, defaulting to 'draft'",
                            title, status)
                status = "draft"

            try:
                try:
                    feature_exist = Feature.objects.get(feature_id=feature_id, deletion_on=None)
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

                new_feature_data = {
                        'title': title,
                        'description' : description,
                        # TODO fix status
                        'status': status,
                        'creator': import_task.user,
                        'project' : feature_type.project,
                        'feature_type' : feature_type,
                        'feature_data' : feature_data,
                    }
                # Ajout conditionnel de 'geom' 
                if feature_type.geom_type != 'none':
                    new_feature_data['geom'] = self.get_geom(feature.get('geometry'))

                current, _ = Feature.objects.update_or_create(
                    feature_id=feature_id,
                    # project=feature_type.project,
                    defaults=new_feature_data
                )
                
            except Exception as er:
                logger.exception(
                    f"L'edition de feature a echoué {er}'. ")
                self.infos.append(
                    f"L'edition de feature a echoué {er}'. ")
                raise GeoJSONProcessingFailed

        # Link similar features based on specific criteria
        self.link_similar_features(current, feature_type)

        if nb_features > 0:
            msg = "{nb} signalement(s) importé(s). ".format(nb=nb_features)
            self.infos.append(msg)

    def check_feature_type(self, features, import_task):
        # Checks if the feature type of incoming features matches the expected type
        feature_type = import_task.feature_type
 
        for feature in features:
            geom = feature.get('geometry')
            if str(geom['type']).lower() != feature_type.geom_type:
                self.infos.append(
                    f"L'edition de feature a echoué. Le type de features sont différents. ")
                raise GeoJSONProcessingFailed

    def check_has_features(self, features):
        # Checks if the features list is empty and raises an exception if so
        if len(features) == 0:
            self.infos.append(
                "Aucun signalement n'est indiqué dans l'entrée 'features'. ")
            raise GeoJSONProcessingFailed

    def validate_data(self, file):
        # Validates and loads data from a provided file, handles JSON decoding
        try:
            up_file = file.read()
            data = json.loads(up_file.decode('utf-8'))
        except Exception as err:
            self.infos.append(
                "Erreur à la lecture du fichier GeoJSON: {} ".format(str(err)))
            raise GeoJSONProcessingFailed
        else:
            return data

    def link_similar_features(self, current_feature, feature_type):
        """
        Searc for similar features based on title, description, and feature type.
        Link them to the new feature as a duplicate.

        Parameters:
        - current_feature: The current feature being processed.
        - feature_type: The feature type object associated with the import task.
        """
        # Filtrer les features par titre, description et type, ou par géométrie et type
        simili_features = Feature.objects.filter(
            Q(title=current_feature.title, description=current_feature.description, feature_type=feature_type)
        )
        # Filtrer les features par géométrie et type si le type de signalement est de type géographique
        if feature_type.geom_type != 'none':
            simili_features = simili_features.filter(
                Q(geom=current_feature.geom, feature_type=feature_type)
            )

        simili_features = simili_features.exclude( 
            # Exclure le feature courant par son ID
            feature_id=current_feature.feature_id
        ).exclude(
            # Exclure les features ayant une date de suppression définie (deletion_on n'est pas None)
            deletion_on__isnull=False
        )

        if simili_features.exists():
            for row in simili_features:
                FeatureLink.objects.get_or_create(
                    relation_type='doublon',
                    feature_from=current_feature,
                    feature_to=row
                )

    def __call__(self, import_task):
    # Main processing method, handles the flow of feature import and updates task status
        try:
            import_task.status = "processing"
            import_task.started_on = timezone.now()
            data = self.validate_data(import_task.file)

            if isinstance(data, dict):
                # Si data est un dictionnaire c'est un geojson, utilisez .get() ou un accès direct
                features = data.get('features')
                self.check_feature_type(features, import_task)
            elif isinstance(data, list):
                # Si data est une liste, c'est un json donc un type de signalement sans géométrie
                features = data
            else:
                self.infos.append("Unexpected data type")
                raise GeoJSONProcessingFailed

            self.check_has_features(features)
            self.create_features(features, import_task)
        except GeoJSONProcessingFailed:
            import_task.status = "failed"
        else:
            import_task.status = "finished"
            import_task.finished_on = timezone.now()
        import_task.infos = "/n".join(self.infos)
        import_task.save(update_fields=['status', 'started_on', 'finished_on', 'infos'])

# Function to initiate GeoJSON processing with an import task
def geojson_processing(import_task):
    process = GeoJSONProcessing()
    process(import_task)
