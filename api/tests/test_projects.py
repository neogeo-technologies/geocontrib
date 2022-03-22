from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.urls import reverse
import pytest

from geocontrib.models.project import Project
from geocontrib.models.user import UserLevelPermission
from geocontrib.models.user import User


@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
def test_projects_list(api_client):
    result = api_client.get('/api/projects/')

    assert result.status_code == 200
    assert result.json() == {'count': 0, 'next': None, 'previous': None, 'results': []}

    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)

    user = User.objects.create(username="usertest")

    anon_perm = UserLevelPermission.objects.get(pk="anonymous")

    p = Project.objects.create(
        title="Projet 1",
        access_level_pub_feature=anon_perm,
        access_level_arch_feature=anon_perm,
        creator=user,
    )
    p.save()

    result = api_client.get('/api/projects/')
    assert result.status_code == 200
    assert result.json() == {
        'count': 1, 
        'next': None, 
        'previous': None, 
        'results': [{
            'title': 'Projet 1', 
            'slug': '2-projet-1', 
            'created_on': '05/08/2021', 
            'updated_on': '05/08/2021', 
            'description': None, 
            'moderation': False, 
            'is_project_type': False, 
            'generate_share_link': False, 
            'thumbnail': '/api/projects/2-projet-1/thumbnail/', 
            'creator': 2,
            'access_level_pub_feature': 'Utilisateur anonyme',
            'access_level_arch_feature': 'Utilisateur anonyme',
            'archive_feature': None,
            'delete_feature': None,
            'nb_features': 0,
            'nb_published_features': 0,
            'nb_comments': 0,
            'nb_published_features_comments': 0,
            'nb_contributors': 1
        }]
    }


@pytest.mark.freeze_time('2021-08-05')
@pytest.mark.django_db(transaction=True)
def test_projects_post(api_client):

    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)

    User.objects.create(username="admin", password="password", is_active=True)
    user = User.objects.create(username="usertest", password="password", is_active=True)
    user.save()

    project_json = dict(
        title="Projet 2",
        access_level_pub_feature="anonymous",
        access_level_arch_feature="anonymous",
        archive_feature=1,
        delete_feature=2,
    )

    api_client.force_authenticate(user=user)

    result = api_client.post('/api/projects/', project_json, format="json")
    assert result.status_code == 201, result.content.decode()
    assert result.json() == {
        'access_level_arch_feature': "anonymous",
        'access_level_pub_feature': "anonymous",
        'archive_feature': 1,
        'creator': user.pk,
        'delete_feature': 2,
        'description': None,
        'is_project_type': False,
        'moderation': False,
        'slug': '3-projet-2',
        'title': 'Projet 2',
    }


@pytest.mark.freeze_time('2021-08-05')
@pytest.mark.django_db(transaction=True)
def test_projects_thumbnail_put(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)

    user = User.objects.create(username="usertest", password="password", is_active=True)
    user.save()
    anon_perm = UserLevelPermission.objects.get(pk="anonymous")
    p = Project.objects.create(
        title="Projet 3",
        access_level_pub_feature=anon_perm,
        access_level_arch_feature=anon_perm,
        creator=user,
    )
    p.save()

    api_client.force_authenticate(user=user)

    filename = 'filename.png'
    with open("test/data/img/image.png", 'rb') as fp:
        simple_file = SimpleUploadedFile(filename,
                                         fp.read(),
                                         content_type='multipart/form-data')

    url = reverse('api:project-thumbnail', kwargs={"slug": "4-projet-3"})


    result = api_client.put(url,
                            {'file':  simple_file})
    assert result.status_code == 200, result.content.decode()
    result_json = result.json()
    thumbnail = result_json.pop('thumbnail')
    assert thumbnail == "/api/projects/4-projet-3/thumbnail/"
    assert result_json == {
        'access_level_arch_feature': 'Utilisateur anonyme',
        'access_level_pub_feature': 'Utilisateur anonyme',
        'archive_feature': None,
        'created_on': '05/08/2021',
        'creator': user.pk,
        'delete_feature': None,
        'description': None,
        'is_project_type': False,
        'generate_share_link': False,
        'moderation': False,
        'nb_comments': 0,
        'nb_contributors': 1,
        'nb_features': 0,
        'nb_published_features': 0,
        'nb_published_features_comments': 0,
        'slug': '4-projet-3',
        'title': 'Projet 3',
        'updated_on': '05/08/2021',
    }

    result = api_client.post(url,
                            {'file':  simple_file})
    assert result.status_code == 405, result.content.decode()
