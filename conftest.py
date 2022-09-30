from pathlib import Path
import json

from django.conf import settings
from rest_framework.test import APIClient

import pytest


@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': f'redis://{ settings.REDIS_HOST }',
        'result_backend': f'redis://{ settings.REDIS_HOST }'
    }


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(scope='session')
def celery_worker_parameters():
    # type: () -> Mapping[str, Any]
    """Redefine this fixture to change the init parameters of Celery workers.

    This can be used e. g. to define queues the worker will consume tasks from.

    The dict returned by your fixture will then be used
    as parameters when instantiating :class:`~celery.worker.WorkController`.
    """
    return {
        # For some reason this `celery.ping` is not registed IF our own worker is still
        # running. To avoid failing tests in that case, we disable the ping check.
        # see: https://github.com/celery/celery/issues/3642#issuecomment-369057682
        # here is the ping task: `from celery.contrib.testing.tasks import ping`
        'perform_ping_check': False,
    }


def verify_or_create_json(filename, json_result, hook=None, sorter=None):

    path = Path(filename)
    if path.exists():
        with path.open(encoding='utf-8') as file:
            json_expected = json.load(file)
            if hook:
                hook(json_expected, json_result)
            if sorter:
                sorter(json_result)
                sorter(json_expected)

            assert json_result == json_expected
    else:
        with path.open("w", encoding='utf-8') as file:
            json.dump(json_result, file)


def verify_or_create(filename, result):

    path = Path(filename)
    if path.exists():
        with path.open('rb') as file:
            expected = file.read()
            assert expected == result
    else:
        with path.open("wb") as file:
            file.write(result)


def sort_features_by_title(data):
    """
    sort geojson by title
    """
    data["features"] = sorted(data.get("features", {}),  key=lambda d: d.get('properties', {}).get('title'))

