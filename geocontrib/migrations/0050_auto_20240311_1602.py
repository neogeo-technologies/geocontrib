# Generated by Django 3.2.25 on 2024-03-11 15:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geocontrib', '0049_projectattribute_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='archive_feature',
        ),
        migrations.RemoveField(
            model_name='project',
            name='delete_feature',
        ),
    ]
