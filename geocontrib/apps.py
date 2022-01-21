from django.apps import AppConfig


class GeocontribConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'geocontrib'

    def ready(self):
        super().ready()
        from . import signals  # NOQA
