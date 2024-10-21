from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.conf import settings

from geocontrib.models import CustomField
from geocontrib.models import FeatureType
from geocontrib.models import Feature

import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = """Permet de générer une vue SQL à la création ou modification d'un type de signalement"""

    def add_arguments(self, parser):
        parser.add_argument('--feature_type_id', type=int, required=True, help='ID of the FeatureType for which to create the view')
        parser.add_argument('--is_deletion', type=bool, required=False, help='Should the view be deleted')
        parser.add_argument('--view_name', type=str, required=False, help='Name of the PostgreSQL view')
        parser.add_argument('--mode', type=str, required=False, help='Mode of the PostgreSQL view')

    def get_custom_fields(self, feature_type_id):
        return CustomField.objects.filter(feature_type__pk=feature_type_id).values()

    def get_all_custom_fields(self, feature_type_ids):
        reference_fields = None  # Used to store the custom fields of the first FeatureType

        for feature_type_id in feature_type_ids:
            # Fetch the custom fields for each feature_type_id
            cfs_data = self.get_custom_fields(feature_type_id)

            # Sort fields by 'name' to ensure consistent comparison
            sorted_cfs = sorted(cfs_data, key=lambda cf: cf['name'])

            if reference_fields is None:
                # Initialize reference fields with the custom fields of the first FeatureType
                reference_fields = sorted_cfs
            else:
                # Compare the custom fields of the current FeatureType with the reference ones
                if len(reference_fields) != len(sorted_cfs) or any(
                    ref['name'] != current['name'] or
                    ref['field_type'] != current['field_type']
                    for ref, current in zip(reference_fields, sorted_cfs)
                ):
                    # Raise a CommandError to stop the command if fields differ
                    raise CommandError(
                        f"Error: Custom fields of FeatureType {feature_type_id} "
                        "do not match the others. Command aborted."
                    )

        return reference_fields  # Return the fields if all are identical


    def handle(self, *args, **options):
        schema = getattr(settings, 'DB_SCHEMA', 'public')  # Get database schema from settings
        feature_type_id = options['feature_type_id']
        mode = options['mode']
        is_deletion = options['is_deletion']
        view_name = options['view_name'] or 'auto_view'

        # Depending on the mode, check that the required Id is specified and build the view name
        if mode == 'Projet':
            # Retrieve project id from the feature type
            feature_type = FeatureType.objects.get(id=feature_type_id)
            project = feature_type.project
            view_name += f'_project_{project.id}'
            
        else:
            view_name += f'_feat_type_{feature_type_id}'

        if is_deletion:
            # Generate SQL to delete the view if it exists
            sql = f"DROP VIEW IF EXISTS {schema}.{view_name}"
        else:
            # Specify the feature fields to display in the view
            feature_fields_selection = ['feature_id', 'title', 'description', 'geom', 'project_id', 'feature_type_id', 'status']
            # Get all existing status choices by default
            status = (stat[0] for stat in Feature.STATUS_CHOICES)
            # Format each field into an object as expected by the SQL template
            fds_data = [{'related_field': field} for field in feature_fields_selection]

            if mode == 'Projet':
                # Get all feature type ids inside the project
                feature_type_ids = list(FeatureType.objects.filter(project=project).values_list('id', flat=True))
                feature_type_ids_str = ', '.join(map(str, feature_type_ids))
                # Retrieve custom fields specific to this project's feature types
                try:
                    # Call function to get and compare custom fields
                    cfs_data = self.get_all_custom_fields(feature_type_ids)
                except CommandError as e:
                    # Output error message if custom fields mismatch and abort command
                    self.stderr.write(str(e))
                    return  # Abort the command if custom fields are not the same

            else:
                # Retrieve custom fields specific to this feature type
                cfs_data = self.get_custom_fields(feature_type_id)

            # Generate the SQL script for creating the PostgreSQL view
            sql = render_to_string(
                'sql/create_view.sql',
                context=dict(
                    fds_data=fds_data,
                    cfs_data=cfs_data,
                    feature_type_ids=feature_type_ids_str if mode == 'Projet' else str(feature_type_id),
                    status=status,
                    schema=schema,
                    view_name=view_name,
                    user=settings.DATABASES['default']['USER'],  # Database user from settings
                ))

        # Log the generated SQL for debugging purposes
        logger.debug(sql)

        try:
            # Execute the SQL script
            self.exec_sql(sql, view_name)
            self.stdout.write(self.style.SUCCESS(f'Successfully {"deleted" if is_deletion else "created"} view {view_name} for FeatureType {feature_type_id}'))
        except Exception as e:
            # Log and raise an error if the view creation fails
            logger.error(f"Error creating view {view_name}: {e}")
            raise CommandError(f"Failed to create view: {str(e)}")

    def exec_sql(self, sql_create_view, view_name):
        from django.db import connections

        success = False
        with connections['default'].cursor() as cursor:
            try:
                # Execute SQL command
                cursor.execute(sql_create_view)
            except Exception as err:
                logger.exception("PostgreSQL view creation failed: {0}".format(sql_create_view))
            else:
                success = True
        return success
