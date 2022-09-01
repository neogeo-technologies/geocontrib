from django.core.management import call_command
from django.urls import reverse
import pytest

from conftest import verify_or_create_json


@pytest.mark.django_db
def test_feature_list(api_client):
    call_command("loaddata", "api/tests/data/test_pre_recorded_values.json", verbosity=0)
    prv_url = reverse('api:list-values', args=["Toulouse Metropole"])
    # Ensure no parameters Fails
    result = api_client.get(prv_url)

    assert result.status_code == 400
    assert result.json() == "Must provide parameter name or pattern."

    result = api_client.get(f'{ prv_url }?pattern=Ly')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_pre_recorded_values_list.json",
                          result.json(),
                         )
