from pathlib import Path
import json

from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
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

@pytest.mark.skip("""
                  Test en echec : il faidrait lancer celery avec la conf de test 
                  ou regarder la doc celery pour le tester

                  On peut lancer le test à la main comme ça
                  curl --user admin:passpass 'http://localhost:8000/api/import-tasks/' -F 'feature_type_slug=1-dfsdfs' -F 'json_file=@api/tests/data/test_features_featuretype_admin.json'
                  et ensuite controller qu'on a bien le même feature type via DRF : http://127.0.0.1:8000/api/features/?feature_type__slug=1-dfsdfs
                  """)
@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
def test_import_post(api_client):
    # Given
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_import_tasks.json", verbosity=0)


    user = User.objects.get(username="admin")
    api_client.force_authenticate(user=user)


    # When importing some features
    # create task
    filename = 'export_projet.json'
    with open("api/tests/data/test_features_featuretype_admin.json", 'rb') as fp:
        simple_file = SimpleUploadedFile(filename,
                                         fp.read(),
                                         content_type='multipart/form-data')
    result = api_client.post('/api/import-tasks/',
                            {
                                "feature_type_slug": "1-dfsdfs",
                                "json_file": simple_file,
                            })
    assert result.status_code == 200

    # run task


    # Then Ensure admin feature type => get all published features of the feature type
    result = api_client.get('/api/features/?feature_type__slug=1-dfsdfs')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_features_featuretype_admin.json", result.json())

