# Generated by Django 4.2 on 2024-10-23 12:37

from django.db import migrations
from django.core.management import call_command
from django.conf import settings

def generate_views_for_existing_data(apps, schema_editor):
    mode = getattr(settings, 'AUTOMATIC_VIEW_CREATION_MODE', 'Type')

    if mode == 'Projet':
        Project = apps.get_model('geocontrib', 'Project')
        for project in Project.objects.all():
            call_command('generate_sql_view', mode='Projet', project_id=project.id)
    else:
        FeatureType = apps.get_model('geocontrib', 'FeatureType')
        for feature_type in FeatureType.objects.all():
            call_command('generate_sql_view', mode='Type', feature_type_id=feature_type.id)


class Migration(migrations.Migration):

    dependencies = [
        ('geocontrib', '0056_merge_20240919_1700'),
    ]

    operations = [
        migrations.RunPython(generate_views_for_existing_data),
    ]
