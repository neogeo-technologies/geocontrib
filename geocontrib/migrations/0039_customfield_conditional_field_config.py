# Generated by Django 3.2.18 on 2023-07-11 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geocontrib', '0038_auto_20230322_1658'),
    ]

    operations = [
        migrations.AddField(
            model_name='customfield',
            name='conditional_field_config',
            field=models.JSONField(blank=True, null=True, verbose_name='Configuration champ conditionnel'),
        ),
    ]