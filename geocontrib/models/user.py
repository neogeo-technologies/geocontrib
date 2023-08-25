import uuid
from enum import Enum, unique
import hashlib

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models
from django.utils import timezone

from geocontrib.choices import ALL_LEVELS


@unique
class Rank(Enum):
    ANONYMOUS = 0
    LOGGED_USER = 1
    CONTRIBUTOR = 2
    SUPER_CONTRIBUTOR = 3
    MODERATOR = 4
    ADMIN = 5


class User(AbstractUser):

    is_administrator = models.BooleanField(
        verbose_name="Est gestionnaire-métier", default=False)
    
    token = models.UUIDField(
        'uuid',
        unique=True,
        default=uuid.uuid4,
        editable=False
    )


class UserLevelPermission(models.Model):
    """
    Les niveaux des permissions pourraient être gérés depuis cette table.
    """

    user_type_id = models.CharField(
        "Identifiant", primary_key=True, choices=ALL_LEVELS, max_length=100)

    rank = models.PositiveSmallIntegerField("Rang", unique=True)

    class Meta:
        verbose_name = "Niveau de permission"
        verbose_name_plural = "Niveaux de permisions"

    def __str__(self):
        return self.get_user_type_id_display()


class Authorization(models.Model):

    def upper_ranks():
        return {"rank__gte": 1}

    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    project = models.ForeignKey('geocontrib.Project', on_delete=models.CASCADE)

    level = models.ForeignKey(
        'geocontrib.UserLevelPermission', on_delete=models.CASCADE,
        limit_choices_to=upper_ranks)

    created_on = models.DateTimeField("Date de création", null=True, blank=True)

    updated_on = models.DateTimeField("Date de modification", null=True, blank=True)

    class Meta:
        # un role par projet
        unique_together = (
            ('user', 'project'),
        )
        verbose_name = 'Autorisation'

    def __str__(self):
        return "{} - {} ({})".format(
            self.user.email, self.project.title, self.level.get_user_type_id_display())

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_on = timezone.now()
        self.updated_on = timezone.now()
        super().save(*args, **kwargs)

    @classmethod
    def get_rank(cls, user, project):

        try:
            auth = cls.objects.get(user=user, project=project)
        except Exception:
            # Si pas d'autorisation defini ou utilisateur non connecté
            user_rank = Rank.LOGGED_USER.value if user.is_authenticated else Rank.ANONYMOUS.value
        else:
            user_rank = auth.level.rank
        return user_rank

    @classmethod
    def get_user_level_projects(cls, user):
        Project = apps.get_model(app_label='geocontrib', model_name="Project")
        UserLevelPermission = apps.get_model(
            app_label='geocontrib', model_name="UserLevelPermission")
        levels = {}
        for project in Project.objects.all():
            levels[project.slug] = UserLevelPermission.objects.get(
                rank=cls.get_rank(user, project)).get_user_type_id_display()
        return levels

    @classmethod
    def get_user_level_projects_ids(cls, user):
        Project = apps.get_model(app_label='geocontrib', model_name="Project")
        level_ids = {}
        for project in Project.objects.all():
            level_ids[project.slug] = cls.get_rank(user, project)
        return level_ids

    @classmethod
    def all_permissions(cls, user, project, feature=None):
        """
        0    ANONYMOUS = 'anonymous'
        1    LOGGED_USER = 'logged_user'
        2    CONTRIBUTOR = 'contributor'
        3    SUPER-CONTRIBUTOR = 'super_contributor'
        4    MODERATOR = 'moderator'
        5    ADMIN = 'admin'
        """
        user_perms = {
            'can_view_project': False,
            'can_create_project': False,  # Redondant avec user.is_administrator
            'can_update_project': False,
            'can_view_feature': False,
            'can_view_archived_feature': False,
            'can_create_feature': False,
            'can_update_feature': False,
            'can_delete_feature': False,
            'can_publish_feature': False,
            'can_create_feature_type': False,
            'can_view_feature_type': False,
            'is_project_super_contributor': False,
            'is_project_moderator': False,
            'is_project_administrator': False,
        }

        if user.is_authenticated and (user.is_superuser or user.is_administrator):
            for k in user_perms.keys():
                user_perms[k] = True
            return user_perms

        else:
            project_rank_min = project.access_level_pub_feature.rank
            project_arch_rank_min = project.access_level_arch_feature.rank

            user_rank = cls.get_rank(user, project)

            if user_rank >= project_rank_min or project_rank_min == Rank.ANONYMOUS.value:
                user_perms['can_view_project'] = True
                user_perms['can_view_feature'] = True
                user_perms['can_view_feature_type'] = True

            # Les contributeurs et utilisateurs de droits supérieurs peuvent créer des features
            if user_rank >= Rank.CONTRIBUTOR.value:
                user_perms['can_create_feature'] = True

            if user_rank == Rank.SUPER_CONTRIBUTOR.value:
                user_perms['can_update_feature'] = True
                user_perms['can_publish_feature'] = True
                user_perms['can_delete_feature'] = True
                user_perms['is_project_super_contributor'] = True

            if user_rank == Rank.MODERATOR.value:
                user_perms['can_publish_feature'] = True
                user_perms['can_create_model'] = True
                user_perms['is_project_moderator'] = True

            if user_rank == Rank.ADMIN.value:
                user_perms['can_publish_feature'] = True
                user_perms['can_update_feature'] = True
                user_perms['can_delete_feature'] = True
                user_perms['can_update_project'] = True
                user_perms['can_create_model'] = True
                user_perms['can_create_feature_type'] = True
                user_perms['is_project_moderator'] = True
                user_perms['is_project_administrator'] = True

            # Visibilité des features archivés
            if user_rank >= project_arch_rank_min:
                user_perms['can_view_archived_feature'] = True

            # On permet à son auteur de modifier un feature s'il est encore contributeur
            # et aux utilisateurs de rangs supérieurs (pour pouvoir modifier le statut
            if (user_rank >= Rank.CONTRIBUTOR.value and (feature and feature.creator == user)):
                user_perms['can_update_feature'] = True

        return user_perms

    @classmethod
    def has_permission(cls, user, permission, project, feature=None):
        auths = cls.all_permissions(user, project, feature)
        if isinstance(auths, dict):
            return auths.get(permission, False)
        return False

class GeneratedToken(models.Model):
    token_sha256= models.CharField("Empreinte SHA256 du username et date de validité", max_length=64)
    expire_on = models.DateTimeField("Timestamp d'expiration du token", blank=True, null=True)
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)

    def save(self, *args, **kwargs):
        self.expire_on = timezone.now() + timezone.timedelta(days=1)
        token_string = self.username + str(self.expire_on)
        self.token_sha256 = hashlib.sha256(token_string.encode('utf-8')).hexdigest()
        super().save(*args, **kwargs)