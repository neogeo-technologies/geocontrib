from django.core.management import call_command
from django.urls import reverse
import pytest

from conftest import verify_or_create_json


@pytest.mark.django_db
def test_list_prerecorded_values_list(api_client):
    prv_url = reverse('api:prerecorded-list-values')
    result = api_client.get(prv_url)
    assert result.status_code == 200

    verify_or_create_json("api/tests/data/test_pre_recorded_values_list_empty.json",
                          result.json(),
                         )

    call_command("loaddata", "api/tests/data/test_pre_recorded_values.json", verbosity=0)

    result = api_client.get(prv_url)
    assert result.status_code == 200

    verify_or_create_json("api/tests/data/test_pre_recorded_values_list_1_element.json",
                          result.json(),
                         )

@pytest.mark.django_db
def test_get_prerecorded_values_list(api_client):
    call_command("loaddata", "api/tests/data/test_pre_recorded_values.json", verbosity=0)

    prv_url = reverse('api:prerecorded-list-values', args=["Toulouse Metropole"])

    result = api_client.get(f'{ prv_url }?pattern=Ly')
    
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_pre_recorded_values_list.json",
                          result.json(),
                         )
