# Generated by Django 3.2.13 on 2022-12-22 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geocontrib', '0032_alter_customfield_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='feature_browsing_default_filter',
            field=models.CharField(blank=True, default='', max_length=20, verbose_name='Filtre par défaut du parcours du signalement'),
        ),
        migrations.AddField(
            model_name='project',
            name='feature_browsing_default_sort',
            field=models.CharField(default='created_on', max_length=20, verbose_name='Tri par défaut du parcours du signalement'),
        ),
    ]
