from pathlib import Path
import json

from django.core.management import call_command
from django.urls import reverse
import pytest

from geocontrib.models.project import Project
from geocontrib.models.user import UserLevelPermission
from geocontrib.models.user import User


def verify_or_create_json(filename, json_result):

    path = Path(filename)
    if path.exists():
        with path.open() as fp:
            json_expected = json.load(fp)
            assert json_expected == json_result
    else:
        with path.open("w") as fp:
            json.dump(json_result, fp)


@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
def test_user(api_client):
    #call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)

    # Ensure not connected 
    url = reverse('api:user-info')

    # result = api_client.get('/api/user_info/')
    result = api_client.get(url)
    assert result.status_code == 403
    verify_or_create_json("api/tests/data/test_user_info_anonymous.json", result.json())

    # Ensure usual user
    user = User.objects.create(username="usertest")
    api_client.force_authenticate(user=user)

    # result = api_client.get('/api/user_info/')
    result = api_client.get(url)
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_user_info_user.json", result.json())

    # Ensure admin
    user = User.objects.create(username="admin", is_administrator=True)
    api_client.force_authenticate(user=user)

    # result = api_client.get('/api/user_info/')
    result = api_client.get(url)
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_user_info_admin.json", result.json())

    # Ensure admin
    user = User.objects.create(username="superuser", is_superuser=True)
    api_client.force_authenticate(user=user)

    # result = api_client.get('/api/user_info/')
    result = api_client.get(url)
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_user_info_superuser.json", result.json())
