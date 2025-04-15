from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.conf import settings
from django.db import connections

from geocontrib.models import CustomField
from geocontrib.models import FeatureType
from geocontrib.models import Feature
from geocontrib.models import Project

import re
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
        parser.add_argument('--feature_type_slug', type=str, required=False, help='Slug of the FeatureType for which to delete the view')
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
        feature_type_slug = options['feature_type_slug']
        project_id = options['project_id']
        mode = options['mode'] or 'Type'
        deleted_cf_id = options['deleted_cf_id']
        schema_name = self.sanitize_schema_name(options['schema_name'] or 'data')

        # Specify the feature fields to display in the view
        feature_fields_selection = ['feature_id', 'title', 'description', 'geom', 'project_id', 'feature_type_id', 'status']
        # Format each field into an object as expected by the SQL template
        fds_data = [{'related_field': field} for field in feature_fields_selection]
        # Get all existing status choices by default
        status = (stat[0] for stat in Feature.STATUS_CHOICES)

        self.create_schema_if_not_exists(schema_name, mode)

        project = self.get_project(project_id, feature_type_id)

        if mode == 'Projet':

            view_name = f"v_{self.safe_view_name(project.slug)}"
            # If deleting a custom field, drop the table, then try to create again
            if deleted_cf_id is not None:
                self.drop_existing_view(schema_name, view_name)

            # Get all feature type ids inside the project
            feature_type_ids = list(FeatureType.objects.filter(project=project).values_list('id', flat=True))

            if feature_type_ids:
                # Prepare a string of ids to pass to the sql template
                feature_type_ids_str = ', '.join(map(str, feature_type_ids))
            else:
                logger.info(f"No feature type found for project {project.slug}")
                return

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

            # On feature type deletion, the slug is accessible in the signal but not within the command, so it's passed as an argument.
            if not feature_type_slug:
                # In other cases, such as custom field signals, the slug isn't directly available, so the ID is generally used instead.
                feature_type_slug = self.get_feature_type(feature_type_id).slug

            view_name = f"v_{self.safe_view_name(feature_type_slug)}__{self.safe_view_name(project.slug)}"

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

    def create_schema_if_not_exists(self, schema_name, mode):
        """
        Create the schema if it doesn't already exist and add a comment to retrieve it if schema_name or mode changes.
        If other schemas containing the comment exist under different names or modes, recreate it with the new schema name and mode.
        """

        schema_comment = f"Schema created automatically by geocontrib in mode"
        # SQL queries
        sql_find_existing_schemas = f"""
            SELECT nspname, obj_description(oid) 
            FROM pg_namespace 
            WHERE obj_description(oid) LIKE '{schema_comment}%';
        """
        sql_create_schema = f"CREATE SCHEMA IF NOT EXISTS {schema_name};"
        sql_add_comment = f"COMMENT ON SCHEMA {schema_name} IS '{schema_comment} {mode}';"
        
        try:
            with connections['default'].cursor() as cursor:
                # Check if a schema with the comment exists
                cursor.execute(sql_find_existing_schemas)
                existing_schemas = cursor.fetchall()
                # Drop all schemas with a name that differs from current schema_name or a different mode
                for existing_schema in existing_schemas:
                    existing_schema_name, existing_comment = existing_schema
                    if existing_schema_name != schema_name or f"mode {mode}" not in existing_comment:
                        logger.warning(f"Dropping schema '{existing_schema_name}'")
                        logger.debug(f"schema_name: '{schema_name}' | mode: '{mode}'")
                        cursor.execute(f"DROP SCHEMA IF EXISTS {existing_schema_name} CASCADE")

                # Create (or recreate) the schema with the current name and add the comment
                cursor.execute(sql_create_schema)
                cursor.execute(sql_add_comment)
        except Exception as e:
            logger.error(f"Error managing schema {schema_name}: {e}")
            raise CommandError(f"Failed to manage schema: {str(e)}")
        
    def safe_view_name(self, slug):
        # Split the slug between the id and the title
        parts = slug.split('-', 1)
        # Check that the first part is an id
        if parts[0].isdigit():
            # Keep only the title
            return f"{parts[1].replace('-', '_')}"
        return slug.replace('-', '_')

    def sanitize_schema_name(self, schema_name: str) -> str:
        """
        Nettoie un nom de schéma pour le rendre compatible avec PostgreSQL.
        
        - Supprime tous les guillemets (simples et doubles).
        - Transforme le nom en minuscules.
        - Remplace les tirets par des underscores.
        - Supprime tous les caractères non autorisés par PostgreSQL.
        - Si le nom commence par un chiffre, préfixe avec un underscore.
        - Tronque à 63 caractères (limite de PostgreSQL).
        
        :param schema_name: Le nom du schéma à nettoyer.
        :return: Un nom de schéma compatible avec PostgreSQL.
        """
        # Supprimer les guillemets simples et doubles
        sanitized = schema_name.replace("'", "").replace('"', "")
        
        # Transformer en minuscules
        sanitized = sanitized.lower()
        
        # Remplacer les tirets par des underscores
        sanitized = sanitized.replace("-", "_")
        
        # Supprimer les caractères non autorisés (seuls les lettres, chiffres et underscores sont autorisés)
        sanitized = re.sub(r"[^a-z0-9_]", "", sanitized)
        
        # Ajouter un underscore si le nom commence par un chiffre
        if sanitized and sanitized[0].isdigit():
            sanitized = f"_{sanitized}"
        
        # Tronquer à 63 caractères (limite de PostgreSQL)
        sanitized = sanitized[:63]
        
        return sanitized


    def get_custom_fields(self, feature_type_id, deleted_cf_id):
        custom_fields = CustomField.objects.filter(feature_type__pk=feature_type_id).values()
        return custom_fields.exclude(id=deleted_cf_id)
    
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

