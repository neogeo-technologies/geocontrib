from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.conf import settings
from django.db import connections

from geocontrib.models import CustomField
from geocontrib.models import FeatureType
from geocontrib.models import Feature
from geocontrib.models import Project

import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    This command generates, modifies, or deletes a PostgreSQL view based on a FeatureType or Project.

    - In 'Projet' mode:
    A view is created or updated for all feature types within a given project. The view will combine all
    feature types with identical attribute structures. If the project contains different feature types with
    mismatched attribute structures, the command will stop to prevent an incorrect representation of the data,
    as mixing attributes from different feature types would lead to a misleading view of the feature types.
    The view is dropped and recreated if necessary, especially when custom fields are modified or deleted.
    
    - In 'Type' mode:
    A view is generated or updated for a single FeatureType. The view is associated with the FeatureType and reflects
    any changes made to the custom fields of that type.
    
    The view schema and name are configurable based on environment variables or command-line options.
    """

    help = """Permet de générer une vue SQL à la création, modification ou suppression d'un type de signalement ou de l'un de ses champs personnalisés"""

    def add_arguments(self, parser):
        parser.add_argument('--feature_type_id', type=int, required=False, help='ID of the FeatureType for which to create the view')
        parser.add_argument('--project_id', type=int, required=False, help='ID of the Project for which to create the view')
        parser.add_argument('--deleted_cf_id', type=int, required=False, help='ID of the deleted custom field to remove from view')
        parser.add_argument('--is_ft_deletion', type=bool, required=False, help='Should the view be deleted')
        parser.add_argument('--schema_name', type=str, required=False, help='Name of the PostgreSQL schema')
        parser.add_argument('--mode', type=str, required=False, help='Mode of the PostgreSQL view')

    def handle(self, *args, **options):
        """
        Main function that handles the generation, modification, or deletion of PostgreSQL views
        for either a single FeatureType or all FeatureTypes within a project.
        """
        is_ft_deletion = options['is_ft_deletion']
        feature_type_id = options['feature_type_id']
        project_id = options['project_id']
        mode = options['mode'] or 'Type'
        deleted_cf_id = options['deleted_cf_id']
        schema_name = options['schema_name'] or 'Data'

        # Specify the feature fields to display in the view
        feature_fields_selection = ['feature_id', 'title', 'description', 'geom', 'project_id', 'feature_type_id', 'status']
        # Format each field into an object as expected by the SQL template
        fds_data = [{'related_field': field} for field in feature_fields_selection]
        # Get all existing status choices by default
        status = (stat[0] for stat in Feature.STATUS_CHOICES)

        self.create_schema_if_not_exists(schema_name)

        if mode == 'Projet':

            # Ensure that either 'project_id' or 'feature_type_id' is provided in 'Projet' mode
            if not project_id and not feature_type_id:
                raise CommandError("You must provide either a 'project_id' or a 'feature_type_id' in 'Projet' mode.")

            project = self.get_project(project_id, feature_type_id)
            view_name = f'project_{project.id}'
            # If deleting a custom field, drop the table, then try to create again
            if deleted_cf_id is not None:
                self.drop_existing_view(schema_name, view_name)

            # Get all feature type ids inside the project
            feature_type_ids = list(FeatureType.objects.filter(project=project).values_list('id', flat=True))

            # Prepare a string of ids to pass to the sql template
            feature_type_ids_str = ', '.join(map(str, feature_type_ids))

            # Retrieve custom fields specific to this project's feature types
            try:
                cfs_data = self.get_all_custom_fields(feature_type_ids, deleted_cf_id)
            except CommandError as e:
                # Output error message if custom fields mismatch and abort command
                logger.debug(e)
                # Delete the previously existing view since the existing one cannot be updated
                self.drop_existing_view(schema_name, view_name)
                return  # Abort the command if custom fields are not the same

        elif mode == 'Type' :

            # Ensure that 'feature_type_id' is provided in 'Type' mode
            if not feature_type_id:
                raise CommandError("You must provide a 'feature_type_id' in 'Type' mode.")

            view_name = f'feature_type_{feature_type_id}'

            if is_ft_deletion:
                # Generate SQL to delete the view if it exists
                self.drop_existing_view(schema_name, view_name)
                return  # Exit the view generation command for this feature type since it was deleted

            # Retrieve custom fields specific to this feature type
            cfs_data = self.get_custom_fields(feature_type_id, deleted_cf_id)

        # Generate the SQL script for creating the PostgreSQL view
        sql = render_to_string(
            'sql/create_view.sql',
            context=dict(
                fds_data=fds_data,
                cfs_data=cfs_data,
                feature_type_ids=feature_type_ids_str if mode == 'Projet' else str(feature_type_id),
                status=status,
                schema=schema_name,
                view_name=view_name,
                user=settings.DATABASES['default']['USER'],  # Database user from settings
            ))
        logger.debug(sql)  # Log the generated SQL for debugging

        its_alright = self.exec_sql(sql, view_name)
        if its_alright:
            logger.info(f'Successfully created view {view_name}')

    def create_schema_if_not_exists(self, schema_name):
        """
        Create the schema if it doesn't already exist.
        """
        sql = f"CREATE SCHEMA IF NOT EXISTS {schema_name};"
        try:
            with connections['default'].cursor() as cursor:
                cursor.execute(sql)
        except Exception as e:
            logger.error(f"Error creating schema {schema_name}: {e}")
            raise CommandError(f"Failed to create schema: {str(e)}")

    def get_custom_fields(self, feature_type_id, deleted_cf_id):
        customFields = CustomField.objects.filter(feature_type__pk=feature_type_id).values()
        return customFields.exclude(id=deleted_cf_id)
    
    def validate_custom_fields(self, reference_fields, sorted_cfs, feature_type_id):
        # Compare the custom fields of the current FeatureType with the reference ones
        if len(reference_fields) != len(sorted_cfs) or any(
            ref['name'] != current['name'] or ref['field_type'] != current['field_type']
            for ref, current in zip(reference_fields, sorted_cfs)
        ):
            # Raise a CommandError to stop the command if fields differ
            raise CommandError(
                f"Error: Custom fields of FeatureType {feature_type_id} "
                "do not match the others. View generation aborted."
            )

    def get_all_custom_fields(self, feature_type_ids, deleted_cf_id):
        reference_fields = None  # Used to store the custom fields of the first FeatureType

        for feature_type_id in feature_type_ids:
            # Fetch the custom fields for each feature_type_id
            cfs_data = self.get_custom_fields(feature_type_id, deleted_cf_id)

            # Sort fields by 'name' to ensure consistent comparison
            sorted_cfs = sorted(cfs_data, key=lambda cf: cf['name'])

            if reference_fields is None:
                # Initialize reference fields with the custom fields of the first FeatureType
                reference_fields = sorted_cfs
            else:
                self.validate_custom_fields(reference_fields, sorted_cfs, feature_type_id)

        return reference_fields  # Return the fields if all are identical

    def drop_existing_view(self, schema_name, view_name):
        sql = f"DROP VIEW IF EXISTS {schema_name}.{view_name}"
        its_alright = self.exec_sql(sql, view_name)
        if its_alright:
            logger.info(f'Successfully deleted view {view_name}')

    def get_feature_type(self, feature_type_id):
        try:
            feature_type = FeatureType.objects.get(id=feature_type_id)
            return feature_type
        except FeatureType.DoesNotExist:
            logger.error(f'Feature type {feature_type_id} does not exist anymore.')
            raise CommandError(f'Project not found for FeatureType {feature_type_id}')

    def get_project(self, project_id, feature_type_id):
        if not project_id:
            # Retrieve project id from the feature type
            feature_type = self.get_feature_type(feature_type_id)
            return feature_type.project
        else:
            return Project.objects.get(id=project_id)

    def exec_sql(self, sql_script, view_name):
        try:
            with connections['default'].cursor() as cursor:
                cursor.execute(sql_script)
            return True
        except Exception as e:
            logger.error(f"Error executing SQL for view {view_name}: {e}")
            return False

