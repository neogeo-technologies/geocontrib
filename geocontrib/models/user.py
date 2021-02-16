from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models
from django.utils import timezone

from geocontrib.choices import ALL_LEVELS


class User(AbstractUser):

    is_administrator = models.BooleanField(
        verbose_name="Est gestionnaire-métier", default=False)


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
            user_rank = 1 if user.is_authenticated else 0
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
    def all_permissions(cls, user, project, feature=None):
        """
        0    ANONYMOUS = 'anonymous'
        1    LOGGED_USER = 'logged_user'
        2    CONTRIBUTOR = 'contributor'
        3    MODERATOR = 'moderator'
        4    ADMIN = 'admin'
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
            'is_project_administrator': False,
        }

        if user.is_superuser:
            for k in user_perms.keys():
                user_perms[k] = True
            return user_perms

        else:
            project_rank_min = project.access_level_pub_feature.rank
            project_arch_rank_min = project.access_level_arch_feature.rank

            user_rank = cls.get_rank(user, project)

            if user_rank >= project_rank_min or project_rank_min == 0:
                user_perms['can_view_project'] = True
                user_perms['can_view_feature'] = True
                user_perms['can_view_feature_type'] = True

            if user_rank >= 4:
                user_perms['can_update_project'] = True
                user_perms['can_create_model'] = True
                user_perms['is_project_administrator'] = True
                user_perms['can_create_feature_type'] = True

            # Visibilité des features archivés
            if user_rank >= project_arch_rank_min:
                user_perms['can_view_archived_feature'] = True

            # On permet à son auteur de modifier un feature s'il est encore contributeur
            # et aux utilisateurs de rangs supérieurs (pour pouvoir modifier le statut
            if (user_rank >= 2 and (feature and feature.creator == user)) or user_rank >= 3:
                user_perms['can_update_feature'] = True

            # On permet à son auteur de modifier un feature s'il est encore contributeur
            # et aux utilisateurs de rangs supérieurs (pour pouvoir modifier le statut
            if (user_rank >= 2 and (feature and feature.creator == user)):
                user_perms['can_delete_feature'] = True

            # Seuls les moderateurs peuvent publier
            if user_rank >= 3:
                user_perms['can_publish_feature'] = True

            # Les contributeurs et utilisateurs de droits supérieurs peuvent créer des features
            if user_rank >= 2:
                user_perms['can_create_feature'] = True

        return user_perms

    @classmethod
    def has_permission(cls, user, permission, project, feature=None):
        auths = cls.all_permissions(user, project, feature)
        if isinstance(auths, dict):
            return auths.get(permission, False)
        return False
