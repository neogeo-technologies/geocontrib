from django.apps import AppConfig


class GeocontribConfig(AppConfig):
    name = 'geocontrib'

    def ready(self):
        super().ready()
        from . import signals  # NOQA
