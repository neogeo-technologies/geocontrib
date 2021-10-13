from celery import shared_task

from django.core.management import call_command


@shared_task()
def task_georchestra_user_sync():
    call_command('georchestra_user_sync')
