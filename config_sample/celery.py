from celery import Celery
from django.conf import settings

app = Celery('geocontrib', broker=settings.CELERY_BROKER_URL)
app.config_from_object('django.conf:settings')
app.autodiscover_tasks()
