import pytest
from django.urls import reverse
from geocontrib.models.user import User
from django.core.management import call_command
from geocontrib.models import Project, Authorization, UserLevelPermission

@pytest.mark.django_db
def test_reader_permissions(api_client):
    # Charger les données de permissions et de projets
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)

    # Authentifier l'utilisateur admin
    user = User.objects.get(username="admin")
    api_client.force_authenticate(user=user)

    # Créer un utilisateur "reader"
    reader_user = User.objects.create(username="reader_user", password="password")
    reader_user.save()

    # Restreindre la visibilité des signalements à contributeur
    project = Project.objects.get(slug="1-aze")
    contrib_level = UserLevelPermission.objects.get(pk="contributor")
    project.access_level_pub_feature = contrib_level
    project.access_level_arch_feature = contrib_level
    project.save()

    # Assigner le rôle "reader" à l'utilisateur pour ce projet
    reader_level = UserLevelPermission.objects.get(pk="reader")
    user_authorization = Authorization.objects.get(user=reader_user, project=project)
    user_authorization.level=reader_level
    user_authorization.save()

    # Authentifier l'utilisateur "reader"
    api_client.logout()
    api_client.force_authenticate(user=reader_user)

    # Appeler l'API pour récupérer les permissions
    url = reverse('api:user-permissions')
    result = api_client.get(url)

    # Vérifier que la réponse est correcte
    assert result.status_code == 200
    permissions = result.json()

    # Vérifier que le projet est présent dans les permissions
    assert "1-aze" in permissions

    # Récupérer les permissions pour le projet
    project_perms = permissions["1-aze"]

    # Vérifier que seules les permissions de lecture sont à True
    assert project_perms["can_view_project"] is True
    assert project_perms["can_view_feature"] is True
    assert project_perms["can_view_feature_type"] is True
    assert project_perms["can_view_archived_feature"] is True

    # Vérifier que toutes les autres permissions sont à False
    assert project_perms["can_create_project"] is False
    assert project_perms["can_update_project"] is False
    assert project_perms["can_create_feature"] is False
    assert project_perms["can_update_feature"] is False
    assert project_perms["can_delete_feature"] is False
    assert project_perms["can_publish_feature"] is False
    assert project_perms["can_create_feature_type"] is False
    assert project_perms["is_project_super_contributor"] is False
    assert project_perms["is_project_moderator"] is False
    assert project_perms["is_project_administrator"] is False
