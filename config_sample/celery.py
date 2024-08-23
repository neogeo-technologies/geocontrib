import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program
# (w/ 'config' as django project name).
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('geocontrib', broker=settings.CELERY_BROKER_URL)
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.broker_connection_retry_on_startup = True