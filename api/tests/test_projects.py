import shutil
import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.conf import settings
from django.core import signing
import pytest

from geocontrib.models import Authorization
from geocontrib.models import Subscription
from geocontrib.models.project import Project
from geocontrib.models.user import User
from geocontrib.models.user import UserLevelPermission
from geocontrib.utils.tokens import generate_subscribe_token
from conftest import verify_or_create_json

@pytest.fixture
def project_default_logo():
    """
    Vérifie qu'il existe un fichier media/default.png qui est utilisé comme logo des projets.
    Si il n'existe pas, il le copie depuis le dossier static
    """
    logo_path = os.path.join(settings.MEDIA_ROOT, "default.png")
    if not os.path.exists(logo_path):
        if not os.path.exists(settings.MEDIA_ROOT):
            os.mkdir(settings.MEDIA_ROOT)
        shutil.copyfile("geocontrib/static/geocontrib/img/default.png", logo_path)


@pytest.mark.django_db(reset_sequences=True)
@pytest.mark.freeze_time('2021-08-05')
def test_projects_list(api_client):
    url = reverse('api:projects-list')
    result = api_client.get(url)

    assert result.status_code == 200
    assert result.json() == {'count': 0, 'next': None, 'previous': None, 'results': []}

    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)

    user = User.objects.create(username="usertest")

    anon_perm = UserLevelPermission.objects.get(pk="anonymous")

    project = Project.objects.create(
        title="Projet 1",
        access_level_pub_feature=anon_perm,
        access_level_arch_feature=anon_perm,
        creator=user,
    )
    project.save()

    result = api_client.get(url)
    assert result.status_code == 200
    assert result.json() == {
        'count': 1,
        'next': None,
        'previous': None,
        'results': [{
            'title': 'Projet 1',
            'slug': '1-projet-1',
            'created_on': '05/08/2021',
            'updated_on': '05/08/2021',
            'description': None,
            'moderation': False,
            'is_project_type': False,
            'generate_share_link': False,
            'fast_edition_mode': False,
            'feature_assignement': False,
            'feature_browsing_default_filter': '',
            'feature_browsing_default_sort': '-created_on',
            'thumbnail': reverse('api:project-thumbnail', args=["1-projet-1"]),
            'creator': 1,
            'access_level_pub_feature': 'Utilisateur anonyme',
            'access_level_arch_feature': 'Utilisateur anonyme',
            'map_max_zoom_level': 22,
            'nb_features': 0,
            'nb_published_features': 0,
            'nb_comments': 0,
            'nb_published_features_comments': 0,
            'nb_contributors': 1,
            'notified_members_at': None,
            'notified_members_by': None,
            'bbox': None,
            'project_attributes':[]
        }]
    }

    Project.objects.create(
        title="Projet 2",
        access_level_pub_feature=anon_perm,
        access_level_arch_feature=anon_perm,
        creator=user,
        is_project_type=True
    )

    # DEPRECATED ENDPOINT API
    url = reverse('api:projects-types-deprecated-list')
    result = api_client.get(url)
    assert result.status_code == 200
    verify_or_create_json('api/tests/data/test_projects_types_list.json', result.json())

    # NEW ENDPOINT API
    url = reverse('api:projects-list') + "?is_project_type=true"
    result = api_client.get(url)
    assert result.status_code == 200
    verify_or_create_json('api/tests/data/test_projects_types_list.json', result.json()['results'])



@pytest.mark.freeze_time('2021-08-05')
@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_projects_post(api_client):

    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)

    User.objects.create(username="admin", password="password", is_active=True)
    user = User.objects.create(username="usertest", password="password", is_active=True)
    user.save()

    project_json = dict(
        title="Projet 2",
        access_level_pub_feature="anonymous",
        access_level_arch_feature="anonymous",
        map_max_zoom_level=20,
    )

    api_client.force_authenticate(user=user)
    url = reverse('api:projects-list')
    result = api_client.post(url, project_json, format="json")

    assert result.status_code == 201, result.content.decode()
    assert result.json() == {
        'access_level_arch_feature': "anonymous",
        'access_level_pub_feature': "anonymous",
        'creator': user.pk,
        'map_max_zoom_level': 20,
        'description': None,
        'is_project_type': False,
        'moderation': False,
        'slug': '1-projet-2',
        'title': 'Projet 2',
        'generate_share_link': False,
        'fast_edition_mode': False,
        'feature_assignement': False,
        'feature_browsing_default_filter': '',
        'feature_browsing_default_sort': '-created_on',
        'project_attributes':[]
    }


@pytest.mark.freeze_time('2021-08-05')
@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_projects_thumbnail(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)

    user = User.objects.create(username="usertest", password="password", is_active=True)
    user.save()
    anon_perm = UserLevelPermission.objects.get(pk="anonymous")
    project = Project.objects.create(
        title="Projet 3",
        access_level_pub_feature=anon_perm,
        access_level_arch_feature=anon_perm,
        creator=user,
    )
    project.save()

    api_client.force_authenticate(user=user)
    filename = 'filename.png'
    with open("api/tests/data/img/image.png", 'rb') as file:
        simple_file = SimpleUploadedFile(filename,
                                         file.read(),
                                         content_type='multipart/form-data')

    url = reverse('api:project-thumbnail', kwargs={"slug": "1-projet-3"})


    result = api_client.put(url,
                            {'file':  simple_file})
    assert result.status_code == 200, result.content.decode()
    result_json = result.json()
    thumbnail = result_json.pop('thumbnail')
    assert thumbnail == url
    assert result_json == {
        'access_level_arch_feature': 'Utilisateur anonyme',
        'access_level_pub_feature': 'Utilisateur anonyme',
        'created_on': '05/08/2021',
        'creator': user.pk,
        'map_max_zoom_level': 22,
        'description': None,
        'is_project_type': False,
        'generate_share_link': False,
        'fast_edition_mode': False,
        'feature_assignement': False,
        'moderation': False,
        'feature_browsing_default_filter': '',
        'feature_browsing_default_sort': '-created_on',
        'nb_comments': 0,
        'nb_contributors': 1,
        'nb_features': 0,
        'nb_published_features': 0,
        'nb_published_features_comments': 0,
        'slug': '1-projet-3',
        'title': 'Projet 3',
        'updated_on': '05/08/2021',
        'notified_members_at': None,
        'notified_members_by': None,
        'bbox': None,
        'project_attributes':[]
    }

    # ensure can't POST
    result = api_client.post(url,
                            {'file':  simple_file})
    assert result.status_code == 405, result.content.decode()

    # ensure can read
    result = api_client.get(url)
    assert result.status_code == 200
    assert result.get('Content-Type') == 'image/png'
    with open("api/tests/data/img/image.png", 'rb') as file:
        # On ne compare que les 512 premiers octest du fichiers
        # (ça suffit pour voir que c'est un PNG)
        assert next(result.streaming_content)[:512] == file.read()[:512]


@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
@pytest.mark.usefixtures('project_default_logo')
def test_project_duplicate(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)

    data = {
        'access_level_arch_feature': 'moderator',
        'access_level_pub_feature': 'anonymous',
        'title': "AZE 2"
    }

    # anon call fails
    url = reverse('api:project-duplicate', args=['1-aze'])
    result = api_client.post(url, data)
    assert result.status_code == 403

    user = User.objects.get(username="admin")
    api_client.force_authenticate(user=user)

    # Ensure no parameters Fails
    result = api_client.post(url)
    assert result.status_code == 400
    assert result.json() == {
        'access_level_arch_feature': ['Ce champ est obligatoire.'],
        'access_level_pub_feature': ['Ce champ est obligatoire.'],
        'title': ['Ce champ est obligatoire.'],
    }

    # ensure it works
    result = api_client.post(url, data, format='json')
    assert result.status_code == 201
    verify_or_create_json('api/tests/data/test_feature_duplicate_create.json', result.json())

    # non existing project fails
    data['title'] = "AZE 3"
    url = reverse('api:project-duplicate', args=['2-aze'])
    result = api_client.post(url, data, format='json')
    assert result.status_code == 404


@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
def test_project_authorization(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)

    data = [
        {
            'level': {
                'codename': 'admin'
            },
            'user': {
                'id': 1
            }
        }
    ]
    url = reverse('api:project-authorization', args=['1-aze'])

    # anon get call success
    result = api_client.get(url)
    assert result.status_code == 200
    assert result.content.decode() == '[]'

    user = User.objects.get(username="admin")
    api_client.force_authenticate(user=user)

    # admin get call success
    result = api_client.get(url)
    assert result.status_code == 200
    assert result.content.decode() == '[]'

    # Ensure no parameters Fails
    result = api_client.put(url, [], format='json')
    assert result.status_code == 400
    assert result.json() == {'error': 'Au moins un administrateur est requis par projet. '}

    # ensure it works
    result = api_client.put(url, data, format='json')
    assert result.status_code == 200
    verify_or_create_json('api/tests/data/test_project_authorization_createjson', result.json())

    # admin get call with data success
    result = api_client.get(url)
    assert result.status_code == 200
    assert result.json() == [
        {
            "user":
            {
                "id":1,
                "first_name":"",
                "last_name":"",
                "username":"admin"
            },
            "level":
            {
                "display":"Administrateur projet",
                "codename":"admin"
            }
        }
    ]

    # non existing project should fail
    url = reverse('api:project-authorization', args=['2-aze'])
    result = api_client.put(url, data, format='json')
    assert result.status_code == 404

    # anon put call should fail
    api_client.logout()
    url = reverse('api:project-authorization', args=['1-aze'])
    result = api_client.put(url, data, format='json')
    assert result.status_code == 403
    assert result.json() == {'detail': "Informations d'authentification non fournies."}

    # test with roles depending on project
    # first create new users
    user = User.objects.create(username="ProjectAdministrator", password="password")
    user.save()
    user = User.objects.create(username="Contributor", password="password")
    user.save()
    user = User.objects.create(username="Moderator", password="password")
    user.save()
    user = User.objects.create(username="SuperContributor", password="password")
    user.save()

    # then give them role by admin
    user = User.objects.get(username="admin")
    api_client.force_authenticate(user=user)

    dataProjAdmin = [
        {
            'level': {
                'codename': 'admin'
            },
            'user': {
                'id': User.objects.get(username="ProjectAdministrator").id
            }
        }
    ]
    api_client.put(url, dataProjAdmin, format='json')

    dataContrib = [
        {
            'level': {
                'codename': 'contributor'
            },
            'user': {
                'id': User.objects.get(username="Contributor").id
            }
        }
    ]
    api_client.put(url, dataContrib, format='json')

    dataModerat = [
        {
            'level': {
                'codename': 'moderator'
            },
            'user': {
                'id': User.objects.get(username="Moderator").id
            }
        }
    ]
    api_client.put(url, dataModerat, format='json')

    dataSuperContr = [
        {
            'level': {
                'codename': 'super_contributor'
            },
            'user': {
                'id': User.objects.get(username="SuperContributor").id
            }
        }
    ]
    api_client.put(url, dataSuperContr, format='json')

    # Project administrator put call should return with data success
    user = User.objects.get(username="ProjectAdministrator")
    api_client.force_authenticate(user=user)
    result = api_client.put(url, data, format='json') # send request
    assert result.status_code == 200
    assert result.json() == [
        {
            "user":
            {
                "id":1,
                "first_name":"",
                "last_name":"",
                "username":"admin"
            },
            "level":
            {
                "display":"Administrateur projet",
                "codename":"admin"
            }
        }
    ]

    # Contributor put call should fail
    user = User.objects.get(username="Contributor")
    api_client.force_authenticate(user=user)
    result = api_client.put(url, data, format='json')
    assert result.status_code == 403
    assert result.json() == {'detail': "Vous n'avez pas la permission d'effectuer cette action."}

    # Moderator put call should fail
    user = User.objects.get(username="Moderator")
    api_client.force_authenticate(user=user)
    result = api_client.put(url, data, format='json')
    assert result.status_code == 403
    assert result.json() == {'detail': "Vous n'avez pas la permission d'effectuer cette action."}

    # SuperContributor put call should fail
    user = User.objects.get(username="SuperContributor")
    api_client.force_authenticate(user=user)
    result = api_client.put(url, data, format='json')
    assert result.status_code == 403
    assert result.json() == {'detail': "Vous n'avez pas la permission d'effectuer cette action."}

@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_notify_project_members_permission(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    anon_perm = UserLevelPermission.objects.get(pk="anonymous")
    # Création des utilisateurs
    admin = User.objects.create(username="ProjectAdministrator", password="password", is_active=True)
    contributor = User.objects.create(username="Contributor", password="password", is_active=True)

    # Création du projet
    project = Project.objects.create(
        title="notify-project-creation-with-subscription",
        access_level_pub_feature=anon_perm,
        access_level_arch_feature=anon_perm,
        creator=admin
    )

    # Cas non autorisé
    api_client.force_authenticate(user=contributor)
    url = reverse('api:notify-project-creation-with-subscription', kwargs={'slug': project.slug})
    response = api_client.post(url)
    assert response.status_code == 403

    # Cas autorisé
    api_client.force_authenticate(user=admin)
    response = api_client.post(url)
    assert response.status_code == 200
    assert response.json() == {"status": "notification_sent"}


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_project_subscribe_by_token(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    anon_perm = UserLevelPermission.objects.get(pk="anonymous")

    # --- Setup : utilisateur et projet ---
    user = User.objects.create(username="Member", password="password", is_active=True)
    project = Project.objects.create(
        title="Test Token Subscription",
        access_level_pub_feature=anon_perm,
        access_level_arch_feature=anon_perm,
        creator=user,
    )
    url = reverse("api:project-subscribe-by-token")

    # --- Cas 1 : Token valide, premier abonnement ---
    payload = {"u": user.id, "p": project.id, "nonce": get_random_string(12)}
    token = signing.dumps(payload, key=settings.SECRET_KEY)
    response = api_client.post(url, {"token": token}, format="json")
    assert response.status_code == 200
    assert response.json()["detail"] == "Member, vous êtes maintenant abonné·e au projet \"Test Token Subscription\"."
    assert Subscription.objects.filter(users=user, project=project).exists()

    # --- Cas 2 : Token valide, utilisateur déjà abonné ---
    response = api_client.post(url, {"token": token}, format="json")
    assert response.status_code == 200
    assert response.json()["detail"] == "Member, vous êtes déjà abonné·e au projet \"Test Token Subscription\"."

    # --- Cas 3 : Token invalide (modifié) ---
    bad_token = token[:-2] + "xx"
    response = api_client.post(url, {"token": bad_token}, format="json")
    assert response.status_code == 400
    assert response.json()["detail"] == "Lien non valide."

    # --- Cas 4 : Utilisateur inexistant (token valide mais user_id invalide) ---
    fake_user_token = signing.dumps(
        {"u": 99999, "p": project.id, "nonce": get_random_string(12)},
        key=settings.SECRET_KEY
    )
    response = api_client.post(url, {"token": fake_user_token}, format="json")
    assert response.status_code == 400  # get_object_or_404 lève une 404

    # --- Cas 5 : Projet inexistant (token valide mais project_id invalide) ---
    fake_project_token = signing.dumps(
        {"u": user.id, "p": 99999, "nonce": get_random_string(12)},
        key=settings.SECRET_KEY
    )
    response = api_client.post(
        reverse("api:project-subscribe-by-token"),
        {"token": fake_project_token},
        format="json"
    )
    assert response.status_code == 404  # get_object_or_404 lève une 404

    # --- Cas 6a : Clé "token" manquante ---
    response = api_client.post(url, {}, format="json")
    assert response.status_code == 400
    assert response.json()["detail"] == "Le token est requis."

    # --- Cas 6b : Clé "token" présente mais valeur vide ---
    response = api_client.post(url, {"token": ""}, format="json")
    assert response.status_code == 400
    assert response.json()["detail"] == "Lien non valide."


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_project_subscribe_by_token_permissions(api_client):
    # Chargement des permissions
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)

    perm_anonymous = UserLevelPermission.objects.get(pk="anonymous")          # rank 0
    perm_logged = UserLevelPermission.objects.get(pk="logged_user")           # rank 1
    perm_contributor = UserLevelPermission.objects.get(pk="contributor")      # rank 2

    # --- Users ---
    user = User.objects.create(username="Utilisateur", password="password", is_active=True)
    admin = User.objects.create(username="admin", password="password", is_active=True)

    # --- Projet ---
    project = Project.objects.create(
        title="Rank Test",
        access_level_pub_feature=perm_anonymous,
        access_level_arch_feature=perm_anonymous,
        creator=admin,
    )

    url = reverse("api:project-subscribe-by-token")

    # ---------------------------------------------------------
    # Cas 1 : utilisateur non-membre (avec rank <= 1) → refusé
    # ---------------------------------------------------------
    payload_rank1 = {"u": user.id, "p": project.id, "nonce": get_random_string(12)}
    token_rank1 = signing.dumps(payload_rank1, key=settings.SECRET_KEY)

    response = api_client.post(url, {"token": token_rank1}, format="json")
    assert response.status_code == 403
    assert response.json()["detail"] == "Utilisateur, vous n'êtes plus membre de ce projet."

    # ---------------------------------------------------------
    # Cas 2 : membre du probjet (avec rank > 1) → OK
    # ---------------------------------------------------------
    Authorization.objects.filter(user=user, project=project).update(level=perm_contributor)  # rank = 2

    payload_rank2 = {"u": user.id, "p": project.id, "nonce": get_random_string(12)}
    token_rank2 = signing.dumps(payload_rank2, key=settings.SECRET_KEY)

    response = api_client.post(url, {"token": token_rank2}, format="json")
    assert response.status_code == 200
    assert response.json()["detail"] == "Utilisateur, vous êtes maintenant abonné·e au projet \"Rank Test\"."
