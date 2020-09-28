from functools import wraps
import os
import uuid

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from geocontrib.choices import ALL_LEVELS
from geocontrib.choices import RELATED_MODELS
from geocontrib.choices import EXTENDED_RELATED_MODELS
from geocontrib.choices import EVENT_TYPES
from geocontrib.choices import STATE_CHOICES
from geocontrib.choices import FREQUENCY_CHOICES
from geocontrib.choices import TYPE_CHOICES
from geocontrib.emails import notif_moderators_pending_features
from geocontrib.emails import notif_creator_published_feature
from geocontrib.managers import AvailableFeaturesManager
from geocontrib.managers import LayerManager

import logging

logger = logging.getLogger(__name__)


#########################
# USER'S RELATED MODELS #
#########################

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


#########################
# BUSINESS LOGIC MODELS #
#########################


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
        UserLevelPermission = apps.get_model(app_label='geocontrib', model_name="UserLevelPermission")
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
            if user_rank >= project_arch_rank_min or project_arch_rank_min < 2:
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


class Project(models.Model):

    def thumbnail_dir(instance, filename):
        return "user_{0}/{1}".format(instance.creator.pk, filename)

    def limit_pub():
        return {"rank__lte": 2}

    def limit_arch():
        # TODO: n'a plus lieu d'etre, les signalements archivés pouvant
        # potentiellement etre visible par tous.
        return {"rank__lte": 4}

    title = models.CharField("Titre", max_length=128, unique=True)

    slug = models.SlugField("Slug", max_length=256, editable=False, null=True)

    created_on = models.DateTimeField("Date de création", blank=True, null=True)

    updated_on = models.DateTimeField("Date de modification", blank=True, null=True)

    description = models.TextField("Description", blank=True, null=True)

    moderation = models.BooleanField("Modération", default=False)

    thumbnail = models.ImageField("Illustration", upload_to=thumbnail_dir, default="default.png")

    creator = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, verbose_name="Créateur",
        on_delete=models.SET_NULL, null=True, blank=True)

    access_level_pub_feature = models.ForeignKey(
        to="geocontrib.UserLevelPermission", limit_choices_to=limit_pub,
        verbose_name="Visibilité des signalements publiés",
        on_delete=models.PROTECT,
        related_name="access_published"
    )

    access_level_arch_feature = models.ForeignKey(
        to="geocontrib.UserLevelPermission", limit_choices_to=limit_arch,
        verbose_name="Visibilité des signalements archivés",
        on_delete=models.PROTECT,
        related_name="access_archived"
    )

    archive_feature = models.PositiveIntegerField(
        "Délai avant archivage", blank=True, null=True)

    delete_feature = models.PositiveIntegerField(
        "Délai avant suppression", blank=True, null=True)

    ldap_project_contrib_groups = ArrayField(
        verbose_name="Groupes LDAP des contributeurs et modérateurs",
        base_field=models.CharField(max_length=256), blank=True, null=True)

    ldap_project_admin_groups = ArrayField(
        verbose_name="Groupes LDAP des administrateurs",
        base_field=models.CharField(max_length=256), blank=True, null=True)

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_on = timezone.now()
        self.updated_on = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('geocontrib:project', kwargs={'slug': self.slug})


class Feature(models.Model):

    STATUS_CHOICES = (
        ("draft", "Brouillon"),
        ("pending", "En attente de publication"),
        ("published", "Publié"),
        ("archived", "Archivé"),
    )

    feature_id = models.UUIDField(
        "Identifiant", primary_key=True, editable=False, default=uuid.uuid4)

    title = models.CharField("Titre", max_length=128, null=True, blank=True)

    description = models.TextField("Description", blank=True, null=True)

    status = models.CharField(
        "Statut", choices=STATUS_CHOICES, max_length=50,
        default="draft")

    created_on = models.DateTimeField("Date de création", null=True, blank=True)

    updated_on = models.DateTimeField("Date de maj", null=True, blank=True)

    archived_on = models.DateField(
        "Date d'archivage automatique", null=True, blank=True)

    deletion_on = models.DateField(
        "Date de suppression automatique", null=True, blank=True)

    creator = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, verbose_name="Créateur",
        on_delete=models.SET_NULL, null=True, blank=True)

    project = models.ForeignKey("geocontrib.Project", on_delete=models.CASCADE)

    feature_type = models.ForeignKey("geocontrib.FeatureType", on_delete=models.CASCADE)

    geom = models.GeometryField("Géométrie", srid=4326)

    feature_data = JSONField(blank=True, null=True)

    objects = models.Manager()

    handy = AvailableFeaturesManager()

    class Meta:
        verbose_name = "Signalement"
        verbose_name_plural = "Signalements"

    def clean(self):
        if self.feature_data and not isinstance(self.feature_data, dict):
            raise ValidationError('Format de donnée invalide')

    def save(self, *args, **kwargs):
        if self._state.adding is True:
            self.created_on = timezone.now()
        self.updated_on = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):

        return reverse('geocontrib:feature_update', kwargs={
            'slug': self.project.slug, 'feature_type_slug': self.feature_type.slug,
            'feature_id': self.feature_id})

    def get_view_url(self):

        return reverse('geocontrib:feature_detail', kwargs={
            'slug': self.project.slug, 'feature_type_slug': self.feature_type.slug,
            'feature_id': self.feature_id})

    @property
    def custom_fields_as_list(self):
        CustomField = apps.get_model(app_label='geocontrib', model_name="CustomField")
        custom_fields = CustomField.objects.filter(feature_type=self.feature_type)
        res = []
        if custom_fields.exists():
            for row in custom_fields.order_by('position').values('name', 'label', 'field_type'):
                value = ''
                if isinstance(self.feature_data, dict):
                    value = self.feature_data.get(row['name'])
                res.append({
                    'label': row['label'],
                    'field_type': row['field_type'],
                    'value': value
                })
        return res

    @property
    def display_creator(self):
        res = "Utilisateur supprimé"
        if self.creator:
            res = self.creator.get_full_name() or self.creator.username
        return res


class FeatureLink(models.Model):
    REL_TYPES = (
        ('doublon', 'Doublon'),
        ('remplace', 'Remplace'),
        ('est_remplace_par', 'Est remplacé par'),
        ('depend_de', 'Dépend de'),
    )
    relation_type = models.CharField(
        'Type de liaison', choices=REL_TYPES, max_length=50, default='doublon')

    # TODO@cbenhabib: a voir si on ne met pas des FK au lieu d'une ref uuid
    feature_from = models.UUIDField(
        "Identifiant du signalement source", max_length=32, blank=True, null=True)
    feature_to = models.UUIDField(
        "Identifiant du signalement lié", max_length=32, blank=True, null=True)

    class Meta:
        verbose_name = "Type de liaison"
        verbose_name_plural = "Types de liaison"


class FeatureType(models.Model):

    GEOM_CHOICES = (
        ("linestring", "Ligne"),
        ("point", "Point"),
        ("polygon", "Polygone"),
    )

    title = models.CharField("Titre", max_length=128)

    slug = models.SlugField("Slug", max_length=256, editable=False, null=True)

    geom_type = models.CharField(
        "Type de géométrie", choices=GEOM_CHOICES, max_length=50,
        default="point")

    color = models.CharField(
        verbose_name='Couleur', max_length=7, blank=True, null=True
    )

    project = models.ForeignKey(
        "geocontrib.Project", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Type de signalement"
        verbose_name_plural = "Types de signalements"

    def save(self, *args, **kwargs):
        if not self.pk and self.title:
            self.created_on = timezone.now()
        self.updated_on = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def is_editable(self):
        Feature = apps.get_model(app_label='geocontrib', model_name="Feature")
        return not Feature.objects.filter(feature_type=self).exists()

# class CustomFieldInterface(models.Model):
#
#     INTERFACE_CHOICES = (
#         ("unique", "Entrée unique"),
#         ("multi_choice", "Choix multiple"),
#         ("radio", "Bouton radio"),
#         ("range", "Curseur"),
#     )
#
#     interface_type = models.CharField(
#         "Type d'interface", choices=INTERFACE_CHOICES, max_length=50,
#         default="unique", null=True, blank=True)
#
#     # Permet de stocker les options des differents type d'input
#     options = ArrayField(base_field=models.CharField(max_length=256), blank=True)
#
#     class Meta:
#         verbose_name = "Interface de champ personnalisé"
#         verbose_name_plural = "Interfaces de champs personnalisés"


class CustomField(models.Model):
    label = models.CharField("Label", max_length=128, null=True, blank=True)

    name = models.CharField("Nom", max_length=128, null=True, blank=True)

    position = models.PositiveSmallIntegerField(
        "Position", default=0, blank=False, null=False)

    field_type = models.CharField(
        "Type de champ", choices=TYPE_CHOICES, max_length=50,
        default="boolean", null=False, blank=False)

    feature_type = models.ForeignKey(
        "geocontrib.FeatureType", on_delete=models.CASCADE
    )

    options = ArrayField(
        base_field=models.CharField(max_length=256), null=True, blank=True)

    # interface = models.ForeignKey(
    #     "geocontrib.CustomFieldInterface", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "Champ personnalisé"
        verbose_name_plural = "Champs personnalisés"
        unique_together = (('name', 'feature_type'),)

    def __str__(self):
        return "{}.{}".format(self.feature_type.slug, self.name)

    def clean(self):

        if self.field_type == 'list' and len(self.options) == 0:
            raise ValidationError("La liste d'options ne peut être vide. ")


class BaseMap(models.Model):
    title = models.CharField('Titre', max_length=256, blank=True, null=True)

    project = models.ForeignKey('geocontrib.Project', on_delete=models.CASCADE)

    layers = models.ManyToManyField('geocontrib.Layer', through='ContextLayer')

    class Meta:
        verbose_name = 'Fond cartographique'
        verbose_name_plural = 'Fonds cartographiques'

    def __str__(self):
        title = self.title or 'N/A'
        return "{0} - ({1})".format(title, self.project)


class ContextLayer(models.Model):

    order = models.PositiveSmallIntegerField("Numéro d'ordre", default=0)

    opacity = models.DecimalField(
        "Opacité",
        max_digits=3,
        decimal_places=2,
        validators=[
            MaxValueValidator(1),
            MinValueValidator(0)
        ],
        default=1)

    base_map = models.ForeignKey(verbose_name="Fond cartographique", to='geocontrib.BaseMap', on_delete=models.CASCADE)

    layer = models.ForeignKey(verbose_name="Couche", to='geocontrib.Layer', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Liaison Fond-Couche'
        verbose_name_plural = 'Liaison Fond-Couche'
        ordering = ('order', )


class Layer(models.Model):
    SCHEMAS = (
        ('wms', 'WMS'),
        ('tms', 'TMS')
    )

    title = models.CharField('Titre', max_length=256, blank=True, null=True)

    service = models.CharField('Service', max_length=256)

    schema_type = models.CharField(
        "Type de couche", choices=SCHEMAS, max_length=50, default="wms")

    options = JSONField("Options", blank=True, null=True)

    objects = models.Manager()

    handy = LayerManager()

    class Meta:
        verbose_name = 'Couche'
        verbose_name_plural = 'Couches'

    def __str__(self):
        title = self.title or ''
        return "{0} - {1} ({2})".format(title, self.service, self.schema_type)


###############################
# FEATURE'S CONTEXTUAL MODELS #
###############################

class AnnotationAbstract(models.Model):

    id = models.UUIDField(
        "Identifiant", primary_key=True, default=uuid.uuid4,
        editable=False)

    created_on = models.DateTimeField(
        "Date de création", blank=True, null=True)

    feature_id = models.UUIDField(
        "Identifiant du signalement", max_length=32, blank=True, null=True)

    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, verbose_name="Auteur",
        on_delete=models.SET_NULL, null=True, blank=True)

    project = models.ForeignKey("geocontrib.Project", on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self._state.adding is True:
            self.created_on = timezone.now()
        super().save(*args, **kwargs)

    @property
    def display_author(self):
        res = "Utilisateur supprimé"
        if self.author:
            res = self.author.get_full_name() or self.author.username
        return res


class Attachment(AnnotationAbstract):

    def attachement_dir(instance, filename):
        return "user_{0}/attachements/{1}".format(instance.author.pk, filename)

    title = models.CharField('Titre', max_length=128)

    info = models.TextField('Info', blank=True, null=True)

    object_type = models.CharField(
        "Type d'objet concerné", choices=RELATED_MODELS, max_length=50)

    # TODO@cbenhabib: valider L'extension + Taille du fichier?
    attachment_file = models.FileField('Pièce jointe', upload_to=attachement_dir)

    # TODO@cbenhabib: si suppression d'un commentaire?
    comment = models.ForeignKey(
        "geocontrib.Comment", on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name = "Pièce jointe"
        verbose_name_plural = "Pièces jointes"

    def __str__(self):
        if self.title:
            return self.title

    @property
    def extension(self):
        name, extension = os.path.splitext(self.attachment_file.name)
        return extension


class Comment(AnnotationAbstract):

    comment = models.TextField('Commentaire', blank=True, null=True)

    feature_type_slug = models.SlugField('Slug du type de signalement', max_length=128)

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"


##########################
# NOTIFICATIONS'S MODELS #
##########################

class Event(models.Model):

    created_on = models.DateTimeField("Date de l'évènement", blank=True, null=True)

    object_type = models.CharField(
        "Type de l'objet lié", choices=EXTENDED_RELATED_MODELS, max_length=100)

    event_type = models.CharField(
        "Type de l'évènement", choices=EVENT_TYPES, max_length=100)

    data = JSONField(blank=True, null=True)

    project_slug = models.SlugField(
        'Slug du projet', max_length=256)

    feature_type_slug = models.SlugField(
        'Slug du type de signalement', max_length=256, blank=True, null=True)

    feature_id = models.UUIDField(
        "Identifiant du signalement", editable=False, max_length=32, blank=True,
        null=True)

    comment_id = models.UUIDField(
        "Identifiant du commentaire", editable=False, max_length=32, blank=True,
        null=True)

    attachment_id = models.UUIDField(
        "Identifiant de la pièce jointe", editable=False, max_length=32,
        blank=True, null=True)

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, verbose_name="Utilisateur", blank=True,
        null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Évènement"
        verbose_name_plural = "Évènements"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_on = timezone.now()
        super().save(*args, **kwargs)

    @property
    def contextualize_action(self):
        evt = 'Aucun evenement'
        obj = 'defini'
        if self.event_type == 'create':
            evt = "Ajout"
        if self.event_type == 'update':
            evt = "Modification"
        if self.event_type == 'delete':
            evt = "Suppression"

        if self.object_type == 'feature':
            obj = "d'un signalement"
        if self.object_type == 'comment':
            obj = "d'un commentaire"
        if self.object_type == 'attachment':
            obj = "d'une piece jointe"

        action = "{} {}".format(evt, obj)
        return action

    def ping_users(self, *args, **kwargs):
        """
        Les différents cas d'envoi de notifications sont :
            - Les modérateurs d’un projet sont notifiés des signalements dont le statut
            devient "pending" (en attente de publication).
            Cela n'a de sens que pour les projets qui sont modérés.

            - L'auteur d'un signalement est notifié des changements de statut du signalement,
            des modifications du signalement et de l’ajout de commentaires
            (si l'auteur n'est pas lui-même à l'origine de ces évènements).

            - Un utilisateur abonné à un projet est notifié de tout évènement
            (dont il n'est pas à l'origine) sur ce projet.
        """
        event_initiator = self.user

        if self.object_type == 'feature':
            feature = Feature.objects.get(feature_id=self.feature_id)
            project = feature.project
            if project.moderation:

                # On notifie les modérateurs du projet si l'evenement concerne
                # Un demande de publication d'un signalement
                feature_status = self.data.get('feature_status', {})
                status_has_changed = feature_status.get('has_changed', False)
                new_status = feature_status.get('new_status', 'draft')

                if status_has_changed and new_status == 'pending':
                    Authorization = apps.get_model(app_label='geocontrib', model_name='Authorization')
                    moderators__emails = Authorization.objects.filter(
                        project=project, level__rank__gte=3
                    ).exclude(
                        user=event_initiator  # On exclue l'initiateur de l'evenement.
                    ).values_list('user__email', flat=True)

                    context = {
                        'feature': feature,
                        'event_initiator': event_initiator,
                    }
                    try:
                        notif_moderators_pending_features(
                            emails=moderators__emails, context=context)
                    except Exception:
                        logger.exception('Event.ping_users')

                # On notifie l'auteur du signalement si l'evenement concerne
                # la publication de son signalement
                if status_has_changed and new_status == 'published':
                    if event_initiator != feature.creator:
                        context = {
                            'feature': feature,
                            'event': self
                        }
                        try:
                            notif_creator_published_feature(
                                emails=[feature.creator.email, ], context=context)
                        except Exception:
                            logger.exception('Event.ping_users.notif_creator_published_feature')


class Subscription(models.Model):

    created_on = models.DateTimeField(
        "Date de création de l'abonnement", blank=True, null=True)

    project = models.ForeignKey(
        "geocontrib.Project", on_delete=models.SET_NULL, blank=True, null=True)

    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, verbose_name="Utilisateurs",
        help_text="Utilisateurs abonnés")

    class Meta:
        verbose_name = "Abonnement"
        verbose_name_plural = "Abonnements"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_on = timezone.now()
        super().save(*args, **kwargs)

    @classmethod
    def is_suscriber(cls, user, project):
        if not user.is_authenticated:
            is_it = False
        else:
            is_it = cls.objects.filter(project=project, users=user.pk).exists()
        return is_it


class StackedEvent(models.Model):

    sending_frequency = models.CharField(
        verbose_name='Fréquence de notification',
        max_length=20,
        blank=True,
        null=True,
        choices=FREQUENCY_CHOICES,
        default='daily',
    )

    state = models.CharField(
        verbose_name="État",
        max_length=20,
        choices=STATE_CHOICES,
        default='pending',
    )
    project_slug = models.SlugField(
        'Slug du projet', max_length=256, blank=True, null=True)

    events = models.ManyToManyField('geocontrib.Event')

    created_on = models.DateTimeField(
        "Date de création du lot", blank=True, null=True)

    updated_on = models.DateTimeField(
        "Date de dernière modification du lot", blank=True, null=True)

    schedualed_delivery_on = models.DateTimeField(
        "Timestamp d'envoi prévu", blank=True, null=True)

    class Meta:
        verbose_name = "Lot de notifications"
        verbose_name_plural = "Lots de notifications des abonnées"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_on = timezone.now()
            if self.sending_frequency == "instantly":
                self.schedualed_delivery_on = timezone.now()
            elif self.sending_frequency == "daily":
                self.schedualed_delivery_on = timezone.now() - timezone.timedelta(days=1)
            elif self.sending_frequency == "weekly":
                self.schedualed_delivery_on = timezone.now() - timezone.timedelta(days=7)
        self.updated_on = timezone.now()
        super().save(*args, **kwargs)


############
# TRIGGERS #
############

def disable_for_loaddata(signal_handler):
    """
    On desactive les trigger pour les loaddata, car ils créent des instances
    redondantes.
    """

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get('raw'):
            return
        signal_handler(*args, **kwargs)
    return wrapper


@receiver(models.signals.post_delete, sender=Project)
@disable_for_loaddata
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Supprime les fichiers image lors de la suppression d'une instance projet.
    """
    if instance.thumbnail and instance.thumbnail.name != 'default.png':
        if os.path.isfile(instance.thumbnail.path):
            os.remove(instance.thumbnail.path)


@receiver(models.signals.pre_delete, sender=User)
@disable_for_loaddata
def anonymize_comments(sender, instance, **kwargs):
    """
    On transfère les commentaires sur un utilisateur anonyme
    """
    if hasattr(instance, 'comments'):
        for comment in instance.comments:
            anonymous, _ = sender.objects.get_or_create(username="anonymous")
            comment.author = anonymous
            comment.save()


@receiver(models.signals.pre_delete, sender=Attachment)
@disable_for_loaddata
def submission_delete(sender, instance, **kwargs):
    instance.attachment_file.delete()


@receiver(models.signals.post_save, sender=FeatureLink)
@disable_for_loaddata
def create_symetrical_relation(sender, instance, created, **kwargs):
    if created:
        if instance.relation_type in ['doublon', 'depend_de']:
            recip = instance.relation_type
        else:
            recip = 'est_remplace_par' if (instance.relation_type == 'remplace') else 'remplace'
        # Creation des réciproques
        sender.objects.update_or_create(
            relation_type=recip,
            feature_from=instance.feature_to,
            feature_to=instance.feature_from)


@receiver(models.signals.post_delete, sender=FeatureLink)
@disable_for_loaddata
def delete_symetrical_relation(sender, instance, **kwargs):
    related = []
    if instance.relation_type in ['doublon', 'depend_de']:
        recip = instance.relation_type
    else:
        recip = 'est_remplace_par' if (instance.relation_type == 'remplace') else 'remplace'
    related = sender.objects.filter(
        relation_type=recip,
        feature_from=instance.feature_to,
        feature_to=instance.feature_from
    )
    # Suppression des réciproques
    for instance in related:
        instance.delete()


@receiver(models.signals.pre_save, sender=Feature)
@disable_for_loaddata
def update_feature_dates(sender, instance, **kwargs):
    if instance.project.archive_feature and instance.project.delete_feature:
        if instance._state.adding and instance.project:
            instance.archived_on = instance.created_on + timezone.timedelta(
                days=instance.project.archive_feature)
            instance.deletion_on = instance.created_on + timezone.timedelta(
                days=instance.project.delete_feature)


@receiver(models.signals.post_save, sender=FeatureType)
@disable_for_loaddata
def slugify_feature_type(sender, instance, created, **kwargs):

    if created:
        instance.slug = slugify("{}-{}".format(instance.pk, instance.title))
        instance.save()


@receiver(models.signals.post_save, sender=Project)
@disable_for_loaddata
def slugify_project(sender, instance, created, **kwargs):

    if created:
        instance.slug = slugify("{}-{}".format(instance.pk, instance.title))
        instance.save()


@receiver(models.signals.post_save, sender=Project)
@disable_for_loaddata
def set_users_perms(sender, instance, created, **kwargs):
    # On ajoute la permission d'admin de projet au créateur
    if created:
        Authorization = apps.get_model(app_label='geocontrib', model_name="Authorization")
        UserLevelPermission = apps.get_model(app_label='geocontrib', model_name="UserLevelPermission")
        User = apps.get_model(app_label='geocontrib', model_name="User")
        try:
            Authorization.objects.create(
                project=instance,
                user=instance.creator,
                level=UserLevelPermission.objects.get(rank=4)
            )
        except Exception:
            logger.exception('Trigger.set_users_perms')
        try:
            for user in User.objects.filter(is_active=True).exclude(pk=instance.creator.pk):
                Authorization.objects.update_or_create(
                    project=instance,
                    user=user,
                    defaults={'level': UserLevelPermission.objects.get(rank=1)}
                )
        except Exception:
            logger.exception('Trigger.set_users_perms')


@receiver(models.signals.post_save, sender=User)
@disable_for_loaddata
def set_auth_member(sender, instance, created, **kwargs):
    Authorization = apps.get_model(app_label='geocontrib', model_name="Authorization")
    UserLevelPermission = apps.get_model(app_label='geocontrib', model_name="UserLevelPermission")
    Project = apps.get_model(app_label='geocontrib', model_name="Project")
    if created:
        try:
            for project in Project.objects.all():
                Authorization.objects.create(
                    project=project,
                    user=instance,
                    level=UserLevelPermission.objects.get(rank=1)
                )
        except Exception:
            logger.exception('Trigger.set_auth_member')
    elif not instance.is_active:
        try:
            for project in Project.objects.all():
                Authorization.objects.update_or_create(
                    project=project,
                    user=instance,
                    defaults={'level': UserLevelPermission.objects.get(rank=0)}
                )
        except Exception:
            logger.exception('Trigger.set_auth_member')


# EVENT'S TRIGGERS

@receiver(models.signals.post_save, sender=Project)
@disable_for_loaddata
def create_event_on_project_creation(sender, instance, created, **kwargs):
    if created:
        Event = apps.get_model(app_label='geocontrib', model_name="Event")
        Event.objects.create(
            user=instance.creator,
            event_type='create',
            object_type='project',
            project_slug=instance.slug,
            data={}
        )


@receiver(models.signals.post_save, sender=Feature)
@disable_for_loaddata
def create_event_on_feature_create(sender, instance, created, **kwargs):
    # Pour la modification d'un signalement l'évènement est generé parallelement
    # à l'update() afin de recupere l'utilisateur courant.
    if created:
        Event = apps.get_model(app_label='geocontrib', model_name="Event")
        Event.objects.create(
            feature_id=instance.feature_id,
            event_type='create',
            object_type='feature',
            user=instance.creator,
            project_slug=instance.project.slug,
            feature_type_slug=instance.feature_type.slug,
            data={
                'extra': instance.feature_data,
                'feature_title': instance.title
            }
        )


@receiver(models.signals.post_save, sender=Comment)
@disable_for_loaddata
def create_event_on_comment_creation(sender, instance, created, **kwargs):
    if created:
        Event = apps.get_model(app_label='geocontrib', model_name="Event")
        Event.objects.create(
            feature_id=instance.feature_id,
            comment_id=instance.id,
            event_type='create',
            object_type='comment',
            user=instance.author,
            project_slug=instance.project.slug,
            feature_type_slug=instance.feature_type_slug,
            data={
                'author': instance.author.get_full_name(),
                'username': instance.author.username,
                'project_slug': instance.project.slug,
                'comment': instance.comment,
            }
        )


@receiver(models.signals.post_save, sender=Attachment)
@disable_for_loaddata
def create_event_on_attachment_creation(sender, instance, created, **kwargs):

    Event = apps.get_model(app_label='geocontrib', model_name="Event")
    # Si creation d'une piece jointe sans rapport avec un commentaire
    if created and not instance.comment:
        Event.objects.create(
            feature_id=instance.feature_id,
            attachment_id=instance.id,
            event_type='create',
            object_type='attachment',
            user=instance.author,
            project_slug=instance.project.slug,
            data={}
        )


@receiver(models.signals.post_save, sender=Event)
@disable_for_loaddata
def notify_or_stack_events(sender, instance, created, **kwargs):

    if created and instance.project_slug and settings.DEFAULT_SENDING_FREQUENCY != 'never':
        # On empile les evenements pour notifier les abonnés, en fonction de la fréquence d'envoi
        StackedEvent = apps.get_model(app_label='geocontrib', model_name="StackedEvent")
        stack, _ = StackedEvent.objects.get_or_create(
            sending_frequency=settings.DEFAULT_SENDING_FREQUENCY, state='pending',
            project_slug=instance.project_slug)
        stack.events.add(instance)
        stack.save()

        # On notifie les collaborateurs des messages nécessitant une action immédiate
        try:
            instance.ping_users()
        except Exception:
            logger.exception('ping_users@notify_or_stack_events')
