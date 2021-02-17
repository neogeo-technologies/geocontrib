from django.apps import AppConfig


class CollabConfig(AppConfig):
    name = 'geocontrib'

    def ready(self):
        super().ready()
        from . import signals  # NOQA
