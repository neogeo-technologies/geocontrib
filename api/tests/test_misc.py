from django.core.management import call_command
from django.urls import reverse
import pytest

from geocontrib.models import Project
from geocontrib.models import Comment
from geocontrib.models import Feature
from geocontrib.models.user import UserLevelPermission
from geocontrib.models.user import User
from conftest import verify_or_create_json


@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
def test_misc_feature_attachement(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)

    # Test feature with no attachements
    features_url = reverse('api:feature-attachments-list', args=['75540f8e-0f4d-4317-9818-cc1219a5df8c'])
    result = api_client.get(features_url)
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_features_attachement_empty.json", result.json())

    # Test add feature to attachements
    user = User.objects.get(username="admin")
    api_client.force_authenticate(user=user)

    attachement = {
        'title': "mon attachement",
        'info': "mon info",
    }

    result = api_client.post(features_url, attachement, format="json")

    assert result.status_code == 201
    res_json = result.json()
    res_json.pop('id')
    verify_or_create_json("api/tests/data/test_misc_features_attachement_create.json", result.json())


@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
def test_misc_project_comments(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)

    # Test feature with no attachements
    features_url = reverse('api:project-comments', args=['1-aze'])
    result = api_client.get(features_url)
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_misc_project_comments_empty.json", result.json())

    user = User.objects.get(username="admin")
    Comment.objects.create(feature_id='75540f8e-0f4d-4317-9818-cc1219a5df8c',
                           author=user,
                           project=Project.objects.get(pk=1),
                           comment="ceci est un commentaire",
                          )


    features_url = reverse('api:project-comments', args=['1-aze'])
    result = api_client.get(features_url)
    assert result.status_code == 200

    verify_or_create_json("api/tests/data/test_misc_project_comments_commented.json", result.json())

    user = User.objects.get(username="admin")
    api_client.force_authenticate(user=user)

    # Test feature with events
    features_url = reverse('api:events-list')
    result = api_client.get(features_url)
    assert result.status_code == 200
    def ignore_comment_ids(expected, result):
        for attachment in ["comments", "events"]:
            for comment in expected[attachment]:
                comment.pop('comment_id')

            for comment in result[attachment]:
                comment.pop('comment_id')

    verify_or_create_json("api/tests/data/test_misc_events_comment.json", result.json(), hook=ignore_comment_ids)


@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
def test_misc_comments_list(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)

    user = User.objects.get(username="admin")
    api_client.force_authenticate(user=user)

    # Test feature with no attachements
    features_url = reverse('api:comments-list', args=['75540f8e-0f4d-4317-9818-cc1219a5df8c'])
    result = api_client.get(features_url)
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_misc_comments_empty.json", result.json())


@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
def test_misc_events_list(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)

    user = User.objects.get(username="admin")
    api_client.force_authenticate(user=user)

    # Test feature with no attachements
    features_url = reverse('api:events-list')
    result = api_client.get(features_url)
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_misc_events_empty.json", result.json())


@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
def test_misc_exif(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)

    from django.core.files.uploadedfile import SimpleUploadedFile


    # Test feature with no attachements
    features_url = reverse('api:exif')
    with open('./geocontrib/exif/test_images/gps/ianare-exif-samples/DSCN0040.jpg', 'rb') as fp:
        result = api_client.post(features_url, {'image_file': fp}, format='multipart')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_misc_exif.json", result.json())

