# Generated by Django 3.2.18 on 2023-07-04 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geocontrib', '0038_auto_20230322_1658'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneratedToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_sha256', models.CharField(max_length=64, verbose_name='Empreinte SHA256 du username et date de validité')),
                ('expire_on', models.DateTimeField(blank=True, null=True, verbose_name="Timestamp d'expiration du token")),
                ('username', models.CharField(max_length=150)),
                ('first_name', models.CharField(blank=True, max_length=30)),
                ('last_name', models.CharField(blank=True, max_length=150)),
                ('email', models.EmailField(blank=True, max_length=254)),
            ],
        ),
    ]
