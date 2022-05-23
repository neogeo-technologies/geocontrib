from time import sleep

from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
import pytest
from conftest import verify_or_create_json
from conftest import sort_features_by_title

from geocontrib.models import User

TIMEOUT = 10


@pytest.mark.freeze_time('2021-08-05')
# Desactive les transaction pour que le worker Celery puisse travailler
@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures('celery_session_app')
@pytest.mark.usefixtures('celery_session_worker')
def test_import_post(api_client):
    # Given
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_import_tasks.json", verbosity=0)

    user = User.objects.get(username="admin")
    api_client.force_authenticate(user=user)
    url = reverse('api:importtask-list')


    # test import list is empty
    result = api_client.get(url)
    assert result.status_code == 200
    assert not result.json()

    # When importing some features
    # create task
    filename = 'export_projet.json'
    with open("api/tests/data/test_features_featuretype_admin.json", 'rb') as file:
        simple_file = SimpleUploadedFile(filename,
                                         file.read(),
                                         content_type='multipart/form-data')
    result = api_client.post(url,
                            {
                                "feature_type_slug": "1-dfsdfs",
                                "json_file": simple_file,
                            })
    assert result.status_code == 200

    status = "pending"
    count = 0
    # run task (wait for finish)
    while status == "pending" and count < TIMEOUT:
        result = api_client.get(url)
        assert result.status_code == 200
        res_json = result.json()

        status = res_json[0]['status']

        count += 1
        sleep(1)

    def ignore_imported_file(expected, result):
        result[0].pop('geojson_file_name')
        result[0].pop('csv_file_name')
        expected[0].pop('geojson_file_name')
        expected[0].pop('csv_file_name')

    verify_or_create_json("api/tests/data/test_import_tasklist.json",
                          res_json,
                          hook=ignore_imported_file)

    # Then Ensure admin feature type => get all published features of the feature type
    url = reverse('api:features-list')
    result = api_client.get(f'{ url }?feature_type__slug=1-dfsdfs')
    assert result.status_code == 200

    def ignore_imported_id(expected, result):
        result['features'][0].pop('id')
        result['features'][1].pop('id')
        expected['features'][0].pop('id')
        expected['features'][1].pop('id')

    verify_or_create_json("api/tests/data/test_import_imported.json",
                          result.json(),
                          sorter=sort_features_by_title,
                          hook=ignore_imported_id)


@pytest.mark.freeze_time('2021-08-05')
# Desactive les transaction pour que le worker Celery puisse travailler
@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures('celery_session_app')
@pytest.mark.usefixtures('celery_session_worker')
def test_import_csv_post(api_client):
    # Given
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_import_tasks.json", verbosity=0)

    user = User.objects.get(username="admin")
    api_client.force_authenticate(user=user)
    url = reverse('api:importtask-list')


    # test import list is empty
    result = api_client.get(url)
    assert result.status_code == 200
    assert not result.json()

    # When importing some features
    # create task
    filename = 'export_projet.json'
    with open("api/tests/data/test_import.csv", 'rb') as file:
        simple_file = SimpleUploadedFile(filename,
                                         file.read(),
                                         content_type='multipart/form-data')
    result = api_client.post(url,
                            {
                                "feature_type_slug": "1-dfsdfs",
                                "csv_file": simple_file,
                            })
    assert result.status_code == 200

    status = "pending"
    count = 0
    # run task
    while status == "pending" and count < TIMEOUT:
        result = api_client.get(url)
        assert result.status_code == 200
        res_json = result.json()

        status = res_json[0]['status']

        count += 1
        sleep(1)

    def ignore_imported_file(expected, result):
        result[0].pop('geojson_file_name')
        result[0].pop('csv_file_name')
        expected[0].pop('geojson_file_name')
        expected[0].pop('csv_file_name')

    verify_or_create_json("api/tests/data/test_import_tasklist.json",
                          res_json,
                          hook=ignore_imported_file)

    # Then Ensure admin feature type => get all published features of the feature type
    url = reverse('api:features-list')
    result = api_client.get(f'{ url }?feature_type__slug=1-dfsdfs')
    assert result.status_code == 200

    def ignore_imported_id(expected, result):
        result['features'][0].pop('id')
        result['features'][1].pop('id')
        expected['features'][0].pop('id')
        expected['features'][1].pop('id')

    verify_or_create_json("api/tests/data/test_import_imported_csv.json",
                          result.json(),
                          sorter=sort_features_by_title,
                          hook=ignore_imported_id)
