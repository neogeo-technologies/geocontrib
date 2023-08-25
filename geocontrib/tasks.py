from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded

from geocontrib import __version__

from geocontrib.models import ImportTask
from geocontrib.utils.geojson import geojson_processing
from geocontrib.utils.csv import csv_processing
from django.core.management import call_command



@shared_task()
def task_geojson_processing(import_task_id):
    try:
        import_task = ImportTask.objects.get(pk=import_task_id)
    except ImportTask.DoesNotExist:
        raise Exception("ImportTask {} not found".format(import_task_id))
    geojson_processing(import_task)

@shared_task()
def task_csv_processing(import_task_id):
    try:
        import_task = ImportTask.objects.get(pk=import_task_id)
    except ImportTask.DoesNotExist:
        raise Exception("ImportTask {} not found".format(import_task_id))
    csv_processing(import_task)


@shared_task()
def task_notify_subscribers():
    call_command('notify_subscribers')


@shared_task(soft_time_limit=2)
def get_geocontrib_version():
    try:
        return __version__
    except SoftTimeLimitExceeded:
        return 'Timeout'
