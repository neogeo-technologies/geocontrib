from celery import shared_task

from geocontrib.models import ImportTask
from geocontrib.utils.geojson import geojson_processing
from django.core.management import call_command


@shared_task()
def task_geojson_processing(import_task_id):
    try:
        import_task = ImportTask.objects.get(pk=import_task_id)
    except ImportTask.DoesNotExist:
        raise Exception("ImportTask {} not found".format(import_task_id))
    geojson_processing(import_task)


@shared_task()
def task_data_cleansing():
    call_command('data_cleansing', 'all')


@shared_task()
def task_notify_subscribers():
    call_command('notify_subscribers')
