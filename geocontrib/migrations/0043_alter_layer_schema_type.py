# Generated by Django 3.2.18 on 2023-10-10 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geocontrib', '0042_featuretype_displayed_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='layer',
            name='schema_type',
            field=models.CharField(choices=[('wms', 'WMS'), ('wmts', 'WMTS'), ('tms', 'TMS')], default='wms', max_length=50, verbose_name='Type de couche'),
        ),
    ]