# Generated by Django 2.2.8 on 2020-07-10 14:13

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geocontrib', '0004_auto_20200707_0936'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contextlayer',
            options={'ordering': ('order',), 'verbose_name': 'Liaison Fond-Couche', 'verbose_name_plural': 'Liaison Fond-Couche'},
        ),
        migrations.AlterField(
            model_name='project',
            name='ldap_project_admin_groups',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=256), blank=True, null=True, size=None, verbose_name='Groupes LDAP des administrateurs'),
        ),
        migrations.AlterField(
            model_name='project',
            name='ldap_project_contrib_groups',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=256), blank=True, null=True, size=None, verbose_name='Groupes LDAP des contributeurs et modérateurs'),
        ),
    ]
