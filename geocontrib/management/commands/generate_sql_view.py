from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.conf import settings

from geocontrib.models import CustomField
from geocontrib.models import Feature

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """Permet de générer une vue SQL à la création ou modification d'un type de signalement"""

    def add_arguments(self, parser):
        parser.add_argument('--feature_type_id', type=int, required=True, help='ID of the FeatureType for which to create the view')
        parser.add_argument('--view_name', type=str, required=True, help='Name of the PostgreSQL view')


    def handle(self, *args, **options):
        feature_type_id = options['feature_type_id']
        view_name = options['view_name']

        # Get specific fields data in features
        feature_detail_initial = [{
            'related_field': (
                str(field.name), "{0} - {1}".format(
                    field.name, field.get_internal_type())),
            'alias': None
        } for field in Feature._meta.get_fields() if field.name in ('feature_id', 'title', 'description', 'geom', 'project_id', 'feature_type_id' 'status')]

        # Transform the original 'fds_data' list to ensure that each item has a simple string field for 'related_field', allowing for compatibility with the SQL template rendering.
        fds_data = [{'related_field': field['related_field'][0], 'alias': field.get('alias', '')} for field in feature_detail_initial]

        cfs_data = CustomField.objects.filter(feature_type__pk=feature_type_id).values()

        status = (stat[0] for stat in Feature.STATUS_CHOICES)

        # Generate SQL script for creating the PostgreSQL view
        sql = render_to_string(
            'sql/create_view.sql',
            context=dict(
                fds_data=fds_data,
                cfs_data=cfs_data,
                feature_type_id=feature_type_id,
                status=status,
                schema=getattr(settings, 'DB_SCHEMA', 'public'),  # Get database schema from settings
                view_name=view_name,
                user=settings.DATABASES['default']['USER'],  # Database user from settings
            ))
        logger.debug(sql)  # Log the generated SQL for debugging

        try:
            # Execute the SQL script
            self.exec_sql(sql, view_name)
            self.stdout.write(self.style.SUCCESS(f'Successfully created view {view_name} for FeatureType {feature_type_id}'))
        except Exception as e:
            logger.error(f"Error creating view {view_name}: {e}")
            raise CommandError(f"Failed to create view: {str(e)}")

    def exec_sql(self, sql_create_view, view_name):
        from django.db import connections

        success = False
        with connections['default'].cursor() as cursor:
            try:
                cursor.execute(sql_create_view)  # Execute SQL command
            except Exception as err:
                logger.exception("PostgreSQL view creation failed: {0}".format(sql_create_view))
            else:
                success = True
        return success