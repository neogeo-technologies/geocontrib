from django.apps import apps


from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

from geocontrib import __version__
from geocontrib.tasks import get_geocontrib_version
from celery.exceptions import TimeoutError


@swagger_auto_schema(
    method='get',
    operation_summary="Get app version",
    tags=["misc"],
    responses={
        200: openapi.Response(
            description="App version",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'geocontrib': openapi.Schema(type=openapi.TYPE_STRING, description="Geocontrib version"),
                    'geocontrib-celery': openapi.Schema(type=openapi.TYPE_STRING, description="Geocontrib Celery version"),
                },
                example={
                    'geocontrib': "1.0.0",
                    'geocontrib-celery': "1.0.0",
                }
            )
        )
    }
)
@api_view(['GET'])
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
