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
def test_feature_list(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)

    # Ensure no parameters Fails
    result = api_client.get('/api/features/')
    assert result.status_code == 400
    assert result.json() == ["Must provide parameter project__slug or feature_type__slug"]

    # Ensure anonymous project => only get published features of the 2 feature types
    result = api_client.get('/api/features/?project__slug=1-aze')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_features_project_anon.json", result.json())

    # Ensure anonymous feature type => only get published features of the feature type
    result = api_client.get('/api/features/?feature_type__slug=1-dfsdfs')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_features_featuretype_anon.json", result.json())


    user = User.objects.get(username="admin")
    api_client.force_authenticate(user=user)
    # Ensure admin project => get all features
    result = api_client.get('/api/features/?project__slug=1-aze')
    assert result.status_code == 200
    # breakpoint()
    verify_or_create_json("api/tests/data/test_features_project_admin.json", result.json())

    # Ensure admin feature type => get all published features of the feature type
    result = api_client.get('/api/features/?feature_type__slug=1-dfsdfs')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_features_featuretype_admin.json", result.json())

    # Ensure wrong project fails
    result = api_client.get('/api/features/?project__slug=1-wrong')
    assert result.status_code == 404

    # Ensure wrong feature_type__slug fails
    result = api_client.get('/api/features/?feature_type__slug=1-wrong')
    assert result.status_code == 404
