from __future__ import absolute_import

# from celery import Task
from celery import shared_task
from celery.utils.log import get_task_logger

# import redis

from geocontrib.utils.geojson import GeoJSONProcessing
from geocontrib.models import ImportTask

logger = get_task_logger(__name__)

# redis_conn = redis.Redis()


# class BaseTaskWithRetry(Task):
#     bind = True
#     autoretry_for = (Exception, )
#     retry_kwargs = {'max_retries': 2, 'countdown': 5}


# @shared_task(base=BaseTaskWithRetry)
@shared_task()
def create_features_from_geojson(import_task_id):
    try:
        import_task = ImportTask.objects.get(pk=import_task_id)
    except ImportTask.DoesNotExist:
        raise Exception("ImportTask {} not found".format(import_task_id))
    geojson_processing = GeoJSONProcessing()
    geojson_processing(import_task)
