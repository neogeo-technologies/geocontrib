from django.apps import apps


from django.http import JsonResponse

from geocontrib import __version__
from geocontrib.tasks import get_geocontrib_version
from celery.exceptions import TimeoutError


def version(request):
    try:
        geocontrib_celeryv = get_geocontrib_version.apply_async().get(timeout=2)
    except TimeoutError:
        geocontrib_celeryv = "Timeout"
        pass

    app_version = {
        'geocontrib': __version__,
        'geocontrib-celery': geocontrib_celeryv
    }

    return JsonResponse(app_version)
