import json

from django.urls import reverse
import pytest
from geocontrib import __version__


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures('celery_session_app')
@pytest.mark.usefixtures('celery_session_worker')
def test_version(api_client):

    url = reverse('api:version')
    result = api_client.get(url)
    assert result.status_code == 200
    assert result.json()['geocontrib'] == __version__
    assert result.json()['geocontrib-celery'] == __version__

