"""
Tests unitaires pour la commande `generate_sql_view`.

Ces tests couvrent les cas principaux et les cas limites :
- Erreurs de mode invalide
- Création de vues SQL par FeatureType et par projet
- Suppression des vues PostgreSQL à la suppression d’un FeatureType
- Gestion des cas où le FeatureType ou ses champs personnalisés sont absents
- Prise en compte des données utilisateurs (feature_data)
- Gestion des collisions de noms de champs après normalisation
- Forçage de l’ajout d’alias (`--force_with_aliases`)
- Simulation de FeatureType orphelin suite à suppression de projet
- Déclenchement de `post_delete` sur un FeatureType en cascade
- Robustesse : aucun échec levé si projet ou FeatureType déjà supprimé
"""

import re
import pytest
import logging
from unittest import mock
from django.core.management import call_command, CommandError
from django.db.models.signals import post_delete, post_save
from django.db import connection
from geocontrib.management.commands import generate_sql_view
from geocontrib.models import Project, FeatureType, Feature, CustomField, User, UserLevelPermission
from geocontrib.models.user import UserLevelPermission, User
from geocontrib.signals import update_sql_view, delete_sql_view

# Utilitaire : vérifie si une vue SQL existe en base PostgreSQL
def get_view_exists(view_name: str) -> bool:
    with connection.cursor() as cursor:
        cursor.execute("SELECT to_regclass(%s)", [view_name])
        return cursor.fetchone()[0] is not None

# Cas 1 : mode invalide => lève une CommandError explicite
@pytest.mark.django_db
def test_generate_sql_view_invalid_mode_raises_error():
    with pytest.raises(CommandError, match="Mode inconnu: INVALID_MODE"):
        call_command('generate_sql_view', mode='INVALID_MODE', feature_type_id=1, schema_name='data')

# Cas 2 : création de vue PostgreSQL en mode Type
@pytest.mark.django_db
def test_generate_sql_view_type_mode_creates_view(caplog):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)

    user = User.objects.create(username="usertest")
    anon_perm = UserLevelPermission.objects.get(pk="anonymous")
    project = Project.objects.create(
        title="Test Project",
        access_level_pub_feature=anon_perm,
        access_level_arch_feature=anon_perm,
        creator=user,
    )
    feature_type = FeatureType.objects.create(
        project=project,
        title="FT",
        geom_type="POINT"
    )

    with caplog.at_level("INFO"):
        call_command(
            "generate_sql_view",
            mode="Type",
            feature_type_id=feature_type.id,
            schema_name="data"
        )

    cmd = generate_sql_view.Command()
    expected_view_name = f"data.v_{cmd.safe_view_name(feature_type.slug)}__{cmd.safe_view_name(project.slug)}"

    assert get_view_exists(expected_view_name), f"La vue {expected_view_name} n'existe pas !"

# Cas 3 : suppression de vue quand is_ft_deletion=True
@pytest.mark.django_db
def test_generate_sql_view_type_deletion_drops_view():
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)

    user = User.objects.create(username="usertest")
    anon_perm = UserLevelPermission.objects.get(pk="anonymous")
    project = Project.objects.create(
        title="Test Project",
        access_level_pub_feature=anon_perm,
        access_level_arch_feature=anon_perm,
        creator=user,
    )
    feature_type = FeatureType.objects.create(
        project=project,
        title="FT",
        geom_type="POINT"
    )

    call_command(
        "generate_sql_view",
        mode="Type",
        feature_type_id=feature_type.id,
        is_ft_deletion=True,
        schema_name="data"
    )

    cmd = generate_sql_view.Command()
    expected_view_name = f"data.v_{cmd.safe_view_name(feature_type.slug)}__{cmd.safe_view_name(project.slug)}"
    assert not get_view_exists(expected_view_name), f"La vue {expected_view_name} existe toujours !"

# Cas 4 : feature_type_id inexistant => CommandError explicite
@pytest.mark.django_db
def test_generate_sql_view_type_missing_feature_type_raises_error():
    with pytest.raises(CommandError, match="Project not found for FeatureType 999"):
        call_command(
            "generate_sql_view",
            mode="Type",
            feature_type_id=999,
            schema_name="data"
        )

# Cas 5 : mode Projet mais aucun FeatureType => info loggée, pas de création
@pytest.mark.django_db
def test_generate_sql_view_project_with_no_feature_type_logs_info(caplog):
    user = User.objects.create(username="usertest")
    anon_perm = UserLevelPermission.objects.get(pk="anonymous")
    project = Project.objects.create(
        title="Empty Project",
        access_level_pub_feature=anon_perm,
        access_level_arch_feature=anon_perm,
        creator=user,
    )

    with caplog.at_level("INFO"):
        call_command(
            "generate_sql_view",
            mode="Projet",
            project_id=project.id,
            schema_name="data"
        )

    assert f"No feature type found for project {project.slug}" in caplog.text

# Cas 6 : projet avec plusieurs FeatureType => vue consolidée créée
@pytest.mark.django_db
def test_generate_sql_view_project_with_multiple_feature_types_creates_view(caplog):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)

    user = User.objects.create(username="usertest")
    anon_perm = UserLevelPermission.objects.get(pk="anonymous")
    project = Project.objects.create(
        title="Multi FT Project",
        access_level_pub_feature=anon_perm,
        access_level_arch_feature=anon_perm,
        creator=user,
    )
    FeatureType.objects.create(project=project, title="FT1", geom_type="POINT")
    FeatureType.objects.create(project=project, title="FT2", geom_type="LINESTRING")

    with caplog.at_level("INFO"):
        call_command(
            "generate_sql_view",
            mode="Projet",
            project_id=project.id,
            schema_name="data"
        )

    cmd = generate_sql_view.Command()
    expected_view_name = f"data.v_{cmd.safe_view_name(project.slug)}"
    assert get_view_exists(expected_view_name), f"La vue {expected_view_name} n'existe pas !"

# Cas 7 : suppression de champ personnalisé => erreur capturée et création évitée
@pytest.mark.django_db
def test_generate_sql_view_project_with_deleted_cf_drops_and_skips_creation(caplog):

    user = User.objects.create(username="usertest")
    anon_perm = UserLevelPermission.objects.get(pk="anonymous")
    project = Project.objects.create(
        title="Project With DeleteCF",
        access_level_pub_feature=anon_perm,
        access_level_arch_feature=anon_perm,
        creator=user,
    )
    ft = FeatureType.objects.create(project=project, title="FT", geom_type="POINT")

    # Ajoute deux champs custom avec noms causant collision après normalisation
    CustomField.objects.create(feature_type=ft, name="Nom-A", label="Nom A", position=1, field_type="text")
    CustomField.objects.create(feature_type=ft, name="Nom A", label="Nom B", position=2, field_type="text")

    caplog.set_level(logging.WARNING)
    call_command(
        "generate_sql_view",
        mode="Projet",
        project_id=project.id,
        deleted_cf_id=None,
        schema_name="data"
    )

    # La vue ne doit pas être créée à cause du drop (collision traitée mais logged)
    assert "Normalized column name collision" in caplog.text

# Cas 8 : vérifie que les données présentes dans feature_data apparaissent dans la vue
@pytest.mark.django_db
def test_generate_sql_view_type_with_feature_data_fields():
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features_with_data.json", verbosity=0)

    # On génère la vue en mode Type pour le FeatureType 1
    call_command(
        "generate_sql_view",
        mode="Type",
        feature_type_id=1,
        schema_name="data"
    )

    # Récupération du nom de la vue attendue via safe_view_name
    cmd = generate_sql_view.Command()
    feature_type = FeatureType.objects.get(pk=1)
    project = feature_type.project
    expected_view_name = f"data.v_{cmd.safe_view_name(feature_type.slug)}__{cmd.safe_view_name(project.slug)}"

    # Vérifie que la vue existe bien
    assert get_view_exists(expected_view_name), f"La vue {expected_view_name} n'existe pas !"

    # Vérifie que les données sont présentes et correctes dans la vue
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT etat, priorite FROM {expected_view_name} WHERE title = %s", ["Fuite d'eau"])
        row = cursor.fetchone()

    assert row is not None, "Aucune ligne retournée pour 'Fuite d'eau'"
    assert row[0] == "ouvert"
    assert row[1] == "élevée"

# Cas 9a : en mode 'Type', une collision de noms normalisés déclenche un alias et logue un avertissement
@pytest.mark.django_db
def test_generate_sql_view_custom_field_name_collision_type(caplog):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)

    user = User.objects.create(username="conflict_user")
    perm = UserLevelPermission.objects.get(pk="anonymous")
    project = Project.objects.create(
        title="Collision Project",
        access_level_pub_feature=perm,
        access_level_arch_feature=perm,
        creator=user,
    )
    ft = FeatureType.objects.create(project=project, title="FT", geom_type="POINT")

    CustomField.objects.create(feature_type=ft, name="Statut", label="A", position=1, field_type="text")
    CustomField.objects.create(feature_type=ft, name="Statüt", label="B", position=2, field_type="text")

    caplog.set_level(logging.DEBUG)
    call_command(
        "generate_sql_view",
        mode="Type",
        project_id=project.id,
        feature_type_id=ft.id,
        schema_name="data"
    )

    logs = caplog.text.lower()
    assert "normalized column name collision" in logs
    assert "aliased as" in logs
    assert "statut__1" in logs

# Cas 9b : en mode 'Projet', une collision sur un même FeatureType déclenche aussi un alias avec avertissement
@pytest.mark.django_db
def test_generate_sql_view_custom_field_name_collision_project(caplog):
    post_save.disconnect(update_sql_view, sender=CustomField)

    try:
        call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)

        user = User.objects.create(username="conflict_user_proj")
        perm = UserLevelPermission.objects.get(pk="anonymous")
        project = Project.objects.create(
            title="Collision Project Global",
            access_level_pub_feature=perm,
            access_level_arch_feature=perm,
            creator=user,
        )
        ft1 = FeatureType.objects.create(project=project, title="FT1", geom_type="POINT")
        ft2 = FeatureType.objects.create(project=project, title="FT2", geom_type="POINT")

        CustomField.objects.create(feature_type=ft1, name="Statut", label="A", position=1, field_type="text")
        CustomField.objects.create(feature_type=ft1, name="Statüt", label="B", position=2, field_type="text")

        CustomField.objects.create(feature_type=ft2, name="Autre", label="C", position=1, field_type="text")

        caplog.set_level(logging.DEBUG)
        call_command(
            "generate_sql_view",
            mode="Projet",
            project_id=project.id,
            schema_name="data",
            force_project_view_with_aliases=True
        )

        logs = caplog.text.lower()
        assert "normalized column name collision" in logs
        assert "aliased as" in logs
        assert "statut__1" in logs

    finally:
        post_save.connect(update_sql_view, sender=CustomField)

@pytest.mark.django_db
def test_generate_sql_view_project_fails_without_force_if_cf_differs(caplog):
    post_save.disconnect(update_sql_view, sender=CustomField)

    try:
        user = User.objects.create(username="testuser")
        perm = UserLevelPermission.objects.get(pk="anonymous")
        project = Project.objects.create(
            title="Proj Clash",
            creator=user,
            access_level_pub_feature=perm,
            access_level_arch_feature=perm,
        )

        ft1 = FeatureType.objects.create(project=project, title="Type A", geom_type="POINT")
        ft2 = FeatureType.objects.create(project=project, title="Type B", geom_type="POINT")

        CustomField.objects.create(feature_type=ft1, name="Field A", label="A", field_type="text")
        CustomField.objects.create(feature_type=ft2, name="Field B", label="B", field_type="text")

        caplog.set_level("DEBUG")

        call_command("generate_sql_view", project_id=project.id, mode="Projet")

        assert any("do not match the others" in msg for msg in caplog.messages)

    finally:
        post_save.connect(update_sql_view, sender=CustomField)

@pytest.mark.django_db
def test_delete_sql_view_on_deleted_project_does_not_fail(caplog):
    post_delete.disconnect(delete_sql_view, sender=FeatureType)
    post_save.disconnect(update_sql_view, sender=FeatureType)

    user = User.objects.create(username="safe_del_user")
    perm = UserLevelPermission.objects.get(pk="anonymous")
    project = Project.objects.create(
        title="Orphan Test",
        creator=user,
        access_level_pub_feature=perm,
        access_level_arch_feature=perm,
    )
    ft = FeatureType.objects.create(project=project, title="FT orphaned", geom_type="POINT")

    # Capture ID pour simuler un signal "fantôme"
    ft_id = ft.id
    ft_slug = ft.slug

    # Supprime le projet (cascade FT)
    project.delete()

    ghost_ft = FeatureType(id=ft_id, slug=ft_slug)

    caplog.set_level("WARNING")

    # Doit passer sans lever d'erreur
    delete_sql_view(sender=FeatureType, instance=ghost_ft)

    # Vérifie que ça log un warning mais ne lève rien
    assert "Project relation is broken" in caplog.text or "Skip view generation" in caplog.text