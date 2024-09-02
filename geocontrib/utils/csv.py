from uuid import uuid4, UUID
import re
import csv
import json
import logging

from django.contrib.gis.geos import GEOSGeometry, Point
from django.contrib.gis.geos.error import GEOSException
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from geocontrib.models import Feature
from geocontrib.models import FeatureLink

logger = logging.getLogger(__name__)

# Custom exception class for handling failures in CSV processing
class CSVProcessingFailed(Exception):
    pass

# Class for processing CSV data
class CSVProcessing:
    """
    This class is designed to process CSV data formats. It can handle scenarios
    where features do not have geographical data ('geom'), following an update to support non-geographical
    feature types. The class provides methods to validate, create, and check features, adapting to the presence
    or absence of geometry data.

    Feature Creation and Validation:
    The class includes methods to create feature instances in the database, validate input data, and handle
    specific attribute processing like generating titles and extracting custom field data.
    """

    def __init__(self, *args, **kwargs):
        self.infos = []

    def get_geom(self, lon, lat):
        # Converts point geometry to GEOSGeometry object, or returns None if conversion fails
        geom = Point(float(lon), float(lat))
        try:
            geom = GEOSGeometry(geom, srid=4326)
        except (GEOSException, ValueError):
            geom = None
        return geom

    def get_feature_data(self, feature_type, properties, field_names):
        # Extracts and returns custom field data from properties based on the feature type
        feature_data = {}
        boolean_as_string = ['True', 'False']
        def adapt_json_string(field_in_feature):
            # Remplacer les occurrences de 'label', ‘label’ ou “label” par "label"
            field_in_feature = re.sub(r"['‘’\"]\s*label\s*['‘’\"]\s*:", '"label":', field_in_feature)
            # Formater les paires clé-valeur pour que les valeurs soient entre guillemets doubles
            field_in_feature = re.sub(r":\s*['‘’\"](.+?)['‘’\"]\s*(?=[,}])", r':"\1"', field_in_feature)
            return field_in_feature

        def convert_to_dict(json_str):
            # Nettoyer la chaîne
            cleaned_str = adapt_json_string(json_str)
            try:
                # Essayer de la convertir en JSON
                json_dict = json.loads(cleaned_str)
                # Accéder à la valeur de 'label' si elle existe
                label_value = json_dict.get('label')
                return label_value
            except json.JSONDecodeError:
                 # Enregistrer l'erreur
                logger.error(f"JSON decode error: {e}")
                # Continuer après avoir enregistré l'erreur
                pass

        # Start processing features
        if hasattr(feature_type, 'customfield_set'):
            for field in field_names:
                value = properties.get(field)
                # check if string value contains a number to avoid converting into number by json.loads, in order to stay consistent with types in the app
                try :
                    float(value)
                    # if no error is raised, we can keep the value as a string and add it to feature_data
                    feature_data[field] = value
                # if ValueError is raised, then it is not a number
                except ValueError:
                    # object and arrays need to be unstringified to keep same format as in the app
                    try:
                        # Vérifier si la chaîne commence par '{'
                        if value.startswith('{'):
                            feature_data[field] = convert_to_dict(value);
                        # Si la chaîne ne commence pas par '{', traiter le cas d'un tableau sous forme d'une string
                        else:
                            feature_data[field] = json.loads(value.replace("'", '"'))
                    except json.decoder.JSONDecodeError:
                        # boolean needs to be unstringified to keep same format as in the app
                        if value in boolean_as_string:
                            feature_data[field] = bool(value)
                        # the rest can stay as a string
                        else:
                            feature_data[field] = value
        return feature_data

    def validate_uuid4(self, id):
        """
        Validates if the provided string is a valid UUID version 4.

        This function attempts to create a UUID object from the given string. If the string is a valid
        hexadecimal code that corresponds to a UUID version 4, the UUID object is successfully created,
        and the function returns True. If the string is not a valid UUID (for instance, due to incorrect
        format or wrong version), a ValueError is raised, and the function returns False.

        Parameters:
        - id (str): The string that needs to be validated as a UUID version 4.

        Returns:
        - bool: True if the string is a valid UUID version 4, False otherwise.
        """
        try:
            # Attempt to create a UUID object from the string.
            val = UUID(id, version=4)
        except ValueError:
            # If a ValueError is raised, it means the string is not a valid UUID version 4.
            return False

        # If no exception was raised, the string is a valid UUID version 4.
        return True

    def handle_title(self, title, feature_id):
        # Handles title generation based on feature_id, generates UUID if both are missing
        if not feature_id or feature_id == '' or (feature_id and not self.validate_uuid4(feature_id)):
            uid = uuid4()
            feature_id = str(uid)
        if not title or title == '':
            title = feature_id
            if not feature_id or feature_id == '':
                title = feature_id
        return title, feature_id
    

    # def detect_csv_dialect(self, filepath):
    #     """
    #     Detects the dialect of a CSV file.

    #     Opens the file and uses csv.Sniffer to determine the delimiter and other
    #     formatting aspects of the CSV file.

    #     Parameters:
    #     - filepath: Path to the CSV file.

    #     Returns:
    #     - A csv.Dialect object representing the detected dialect of the CSV file.
    #     """
    #     with open(filepath, 'r') as csvfile:
    #         dict_reader = csv.DictReader(csvfile)
    #         header_output = dict_reader.fieldnames
    #         sniffer = csv.Sniffer()
    #         dialect = sniffer.sniff(json.dumps(header_output))
    #     return dialect

    def process_feature_row(self, feature, feature_type, field_names, creator):
        """
        Processes a single row from the CSV file and prepares data for feature creation or update.

        Parameters:
        - feature: A dictionary representing a single row from the CSV.
        - feature_type: The feature type object associated with the import task.
        - field_names: List of custom field names for the feature type.
        - creator: User instance representing the creator of the feature.

        Returns:
        - A dictionary with prepared data for creating or updating a Feature object.
        - A string representing the feature ID.
        """
        feature_data = self.get_feature_data(feature_type, feature, field_names)
        title, feature_id = self.handle_title(feature.get("title"), feature.get("id"))
        description = feature.get('description')
        status = self.get_valid_status(title, feature.get('status'))

        new_feature_data = {
            'title': title,
            'description': description,
            'status': status,
            'creator': creator,
            'project': feature_type.project,
            'feature_type': feature_type,
            'feature_data': feature_data,
        }

        if feature_type.geom_type != 'none':
            new_feature_data['geom'] = self.get_geom(feature.get('lon'), feature.get('lat'))

        return new_feature_data, feature_id

    def get_valid_status(self, title, status):
        """
        Validates and returns a valid status for a feature.

        If the provided status is not within the allowed choices, defaults to 'draft'.

        Parameters:
        - status: The status value to be validated.

        Returns:
        - A string representing a valid status.
        """
        if status not in [choice[0] for choice in Feature.STATUS_CHOICES]:
            logger.warn(f"Feature '{title}' import: Unknown status '{status}' provided, defaulting to 'draft'")
            return "draft"
        return status

    @transaction.atomic
    def create_features(self, import_task, data):
        """
        Processes CSV data and creates or updates features based on its content.

        Processes each row from the provided CSV data,
        and creates or updates feature records in the database.

        Parameters:
        - import_task: An instance of the ImportTask model containing the CSV file and related data.
        - data: The validated and loaded CSV data.

        Raises:
        - CSVProcessingFailed: If any errors occur during processing of the CSV data.
        """
        if not data:
            self.infos.append("Aucun signalement trouvé dans le fichier CSV.")
            raise CSVProcessingFailed

        feature_type = import_task.feature_type
        field_names = feature_type.customfield_set.values_list('name', flat=True)

        for feature in data:
            new_feature_data, feature_id = self.process_feature_row(
                feature, feature_type, field_names, import_task.user
            )
            self.create_or_update_feature(feature_id, new_feature_data, feature_type)
        
        self.log_feature_import(len(data))


    def create_or_update_feature(self, feature_id, new_feature_data, feature_type):
        """
        Creates or updates a feature in the database.

        This method checks if a feature with the given ID already exists. If it does, and if the existing feature
        belongs to a different project or feature type than the one being imported, the method resets the feature_id
        to None. This ensures that a new feature is created instead of updating an unrelated existing feature.
        The method then creates or updates the feature in the database.

        Parameters:
        - feature_id: The ID of the feature to create or update.
        - new_feature_data: Dictionary containing data for the feature.
        - feature_type: The feature type object associated with the import task.

        Raises:
        - CSVProcessingFailed: If any errors occur during creation or update of the feature.
        """
        try:
            # Check if the feature with the provided ID already exists
            try:
                feature_exist = Feature.objects.get(feature_id=feature_id, deletion_on=None)
            except Feature.DoesNotExist:
                feature_exist = None
                # The CSV might come with an old ID. We reset the ID here as well.
                feature_id = None

            # Reset feature_id if the existing feature is in a different project or feature type
            if feature_exist:
                if feature_exist.project != feature_type.project or feature_exist.feature_type != feature_type:
                    # If the ID from the import exists, but we wish to create the feature in another project,
                    # we set the ID to None
                    feature_id = None

            # Create or update the feature in the database
            current, _ = Feature.objects.update_or_create(
                feature_id=feature_id,
                defaults=new_feature_data
            )

            # Link similar features based on specific criteria
            self.link_similar_features(current, feature_type)

        except Exception as er:
            logger.exception(f"L'edition ou creation de feature a echoué: {er}.")
            self.infos.append(f"L'edition ou creation de feature a echoué: {er}.")
            raise CSVProcessingFailed


    def link_similar_features(self, current_feature, feature_type):
        """
        Search for similar features based on title, description, and feature type.
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


    def log_feature_import(self, count):
        """
        Logs the number of features imported.

        Parameters:
        - count: The number of features processed.
        """
        if count > 0:
            msg = "{nb} signalement(s) importé(s). ".format(nb=count)
            self.infos.append(msg)
        
    def validate_data(self, file):
        """
        Validates and loads data from a CSV file.

        Opens the provided CSV file, uses csv.Sniffer to detect the file's dialect,
        and then reads the data using csv.DictReader.

        Parameters:
        - file: A file object representing the CSV file to be processed.

        Returns:
        - A list of dictionaries, each representing a row in the CSV file.

        Raises:
        - CSVProcessingFailed: If any errors occur during reading or parsing of the CSV file.
        """
        try:
            # Open the CSV file for reading
            with open(file.path, 'r') as csvfile:
                # Use csv.Sniffer to detect the dialect of the CSV file
                sniffer = csv.Sniffer()
                # Read the first 10000 characters of the file to detect the CSV dialect.
                # This sample size has been increased to be sufficent to accurately determine delimiter within CSV file containing long lines
                dialect = sniffer.sniff(csvfile.read(10000))

                # Reset the file pointer back to the start of the file after sniffing.
                # This ensures that when we process the file, we start from the beginning, including the part read for sniffing.
                csvfile.seek(0)

                # Read the CSV data using the detected dialect
                reader = csv.DictReader(csvfile, dialect=dialect)
                # Convert the read data into a list of dictionaries
                data = list(reader)
        except Exception as err:
            # Log and raise an error if any issues occur while reading the CSV
            logger.warn(type(err), err)
            self.infos.append("Erreur à la lecture du fichier CSV: {} ".format(str(err)))
            raise CSVProcessingFailed
        else:
            # Return the loaded data if successful
            return data


    def __call__(self, import_task):
    # Main processing method, handles the flow of feature import and updates task status
        try:
            import_task.status = "processing"
            import_task.started_on = timezone.now()

            # Validation and loading of CSV data
            data = self.validate_data(import_task.file)

            # Proceed with creating features if data is valid
            self.create_features(import_task, data)

        except CSVProcessingFailed as err:
            logger.warn('%s' % type(err))
            import_task.status = "failed"
        else:
            import_task.status = "finished"
            import_task.finished_on = timezone.now()
        import_task.infos = "/n".join(self.infos)
        import_task.save(update_fields=['status', 'started_on', 'finished_on', 'infos'])


# Function to initiate CSV processing with an import task
def csv_processing(import_task):
    process = CSVProcessing()
    process(import_task)
