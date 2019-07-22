import os
import uuid

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse

from collab.choices import ALL_LEVELS
from collab.choices import RELATED_MODELS
from collab.choices import EXTENDED_RELATED_MODELS
from collab.choices import EVENT_TYPES
from collab.choices import STATE_CHOICES
from collab.choices import FREQUENCY_CHOICES
from collab.managers import AvailableFeaturesManager


import logging
logger = logging.getLogger('django')


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

    project = models.ForeignKey('collab.Project', on_delete=models.CASCADE)

    level = models.ForeignKey(
        'collab.UserLevelPermission', on_delete=models.CASCADE,
        limit_choices_to=upper_ranks)

    created_on = models.DateTimeField("Date de création", null=True, blank=True)

    updated_on = models.DateTimeField("Date de modification", null=True, blank=True)

    class Meta:
        # un role par projet
        unique_together = (
            ('user', 'project'),
        )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_on = timezone.now()
        self.updated_on = timezone.now()
        super().save(*args, **kwargs)

    @classmethod
    def get_rank(cls, user, project):

        # Si pas d'autorisation defini ou utilisateur non connecté
        try:
            auth = cls.objects.get(user=user, project=project)
        except Exception:
            user_rank = 1 if user.is_authenticated else 0
        else:
            user_rank = auth.level.rank
        return user_rank

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
            'can_create_project': False,  # Redondant avec user.is_administartor
            'can_update_project': False,
            'can_view_feature': False,
            'can_create_feature': False,
            'can_update_feature': False,
            'can_publish_feature': False,
            'can_archive_feature': False,
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

            if user_rank >= project_rank_min or project_rank_min < 2:
                user_perms['can_view_project'] = True
                user_perms['can_view_feature'] = True
                user_perms['can_view_feature_type'] = True

            if user_rank >= 4:
                user_perms['can_update_project'] = True
                user_perms['can_create_model'] = True
                user_perms['is_project_administrator'] = True

            if user_rank >= project_arch_rank_min or project_arch_rank_min < 2:
                user_perms['can_archive_feature'] = True

            # on permet aux utilisateur de modifier leur propre feature
            if user_rank >= 3 or (feature and feature.user == user):
                user_perms['can_update_feature'] = True

            # seuls les moderateurs peuvent publier
            if user_rank >= 3:
                user_perms['can_publish_feature'] = True
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
        return {"rank__gt": 2}

    title = models.CharField("Titre", max_length=128, unique=True)

    slug = models.SlugField("Slug", max_length=256, editable=False, null=True)

    created_on = models.DateTimeField("Date de création", blank=True, null=True)

    description = models.TextField("Description", blank=True, null=True)

    moderation = models.BooleanField("Modération", default=False)

    thumbnail = models.ImageField("Illustration", upload_to=thumbnail_dir, default="default.png")

    creator = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, verbose_name="Créateur",
        on_delete=models.SET_NULL, null=True, blank=True)

    access_level_pub_feature = models.ForeignKey(
        to="collab.UserLevelPermission", limit_choices_to=limit_pub,
        verbose_name="Visibilité des signalements publiés",
        on_delete=models.PROTECT,
        related_name="access_published"
    )

    access_level_arch_feature = models.ForeignKey(
        to="collab.UserLevelPermission", limit_choices_to=limit_arch,
        verbose_name="Visibilité des signalements archivés",
        on_delete=models.PROTECT,
        related_name="access_archived"
    )

    archive_feature = models.PositiveIntegerField(
        "Délai avant archivage", blank=True, null=True)

    delete_feature = models.PositiveIntegerField(
        "Délai avant suppression", blank=True, null=True)

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_on = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('collab:project', kwargs={'slug': self.slug})


class Feature(models.Model):
    """
    On reprend ici les champs standards augmentés de champs optionnels
    multiples génériques.
    """

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
        default="draft", null=True, blank=True)

    created_on = models.DateTimeField("Date de création", null=True, blank=True)

    updated_on = models.DateTimeField("Date de maj", null=True, blank=True)

    archived_on = models.DateField(
        "Date d'archivage automatique", null=True, blank=True)

    deletion_on = models.DateField(
        "Date de suppression automatique", null=True, blank=True)

    creator = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, verbose_name="Créateur",
        on_delete=models.SET_NULL, null=True, blank=True)

    project = models.ForeignKey("collab.Project", on_delete=models.CASCADE)

    feature_type = models.ForeignKey("collab.FeatureType", on_delete=models.CASCADE)

    geom = models.GeometryField("Géométrie", srid=settings.DB_SRID, blank=True, null=True)

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

    @property
    def custom_fields_as_list(self):
        CustomField = apps.get_model(app_label='collab', model_name="CustomField")
        custom_fields = CustomField.objects.filter(feature_type=self.feature_type)
        res = []
        if custom_fields.exists():
            for row in custom_fields.order_by('position').values('name', 'label', 'field_type'):
                res.append({
                    'label': row['label'],
                    'field_type': row['field_type'],
                    'value': self.feature_data.get(row['name'])
                })
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
        default="boolean")

    project = models.ForeignKey(
        "collab.Project", on_delete=models.CASCADE)

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

# Si besoin de garder les valeurs en base
# class CustomFieldValue(models.Model):
#
#     label = models.CharField("Label", max_length=128, null=True, blank=True)
#
#     name = models.CharField("Name", max_length=128, null=True, blank=True)
#
#     position = models.PositiveIntegerField("Position", null=True, blank=True)
#
#     custom_field = models.ForeignKey(
#         "collab.CustomField", on_delete=models.CASCADE, blank=True, null=True)
#
#     class Meta:
#         verbose_name = "Valeur de champ personnalisé"
#         verbose_name_plural = "Valeurs de champs personnalisés"


class CustomField(models.Model):

    TYPE_CHOICES = (
        ("boolean", "Booléen"),
        ("char", "Chaîne de caractères"),
        ("date", "Date"),
        ("integer", "Entier"),
        ("decimal", "Décimale"),
        ("text", "Champ texte"),
    )

    label = models.CharField("Label", max_length=128, null=True, blank=True)

    name = models.CharField("Nom", max_length=128, null=True, blank=True)

    position = models.PositiveSmallIntegerField(
        "Position", default=0, blank=False, null=False)

    field_type = models.CharField(
        "Type de champ", choices=TYPE_CHOICES, max_length=50,
        default="boolean", null=True, blank=True)

    feature_type = models.ForeignKey(
        "collab.FeatureType", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Champ personnalisé"
        verbose_name_plural = "Champs personnalisés"
        unique_together = (('name', 'feature_type'), )

    def __str__(self):
        return "{}.{}".format(self.feature_type.slug, self.name)


class Layer(models.Model):
    SCHEMAS = (
        ('wms', 'WMS'),
        ('tms', 'TMS')
    )
    name = models.CharField('Nom', max_length=256, blank=True, null=True)

    title = models.CharField('Titre', max_length=256, blank=True, null=True)

    style = models.CharField('Style', max_length=256, blank=True, null=True)

    service = models.URLField('Service')

    order = models.PositiveSmallIntegerField("Numéro d'ordre", default=0)

    schema_type = models.CharField(
        "Type de couche", choices=SCHEMAS, max_length=50, default="wms")

    project = models.ForeignKey('collab.Project', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Couche'
        verbose_name_plural = 'Couches'
        unique_together = ('project', 'order')

    def __str__(self):
        if self.title:
            return " ".format(self.pk, self.title)
        else:
            return "{}- {}".format(self.pk, self.service[0:25])


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
        to=settings.AUTH_USER_MODEL, verbose_name="Auteur", on_delete=models.CASCADE)

    project = models.ForeignKey("collab.Project", on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self._state.adding is True:
            self.created_on = timezone.now()
        super().save(*args, **kwargs)


class Attachment(AnnotationAbstract):

    def attachement_dir(instance, filename):
        return "user_{0}/attachements/{1}".format(instance.author.pk, filename)

    title = models.CharField('Titre', max_length=128)

    info = models.TextField('Info', blank=True, null=True)

    type_objet = models.CharField(
        "Type d'objet concerné", choices=RELATED_MODELS, max_length=50)

    # TODO@cbenhabib: valider L'extension + Taille du fichier?
    attachment_file = models.FileField('Pièce jointe', upload_to=attachement_dir)

    # TODO@cbenhabib: si suppression d'un commentaire?
    comment = models.ForeignKey(
        "collab.Comment", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "Pièce jointe"
        verbose_name_plural = "Pièces jointes"

    def __str__(self):
        if self.title:
            return self.title


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

    feature_id = models.UUIDField(
        "Identifiant du signalement", editable=False, max_length=32, blank=True,
        null=True)

    comment_id = models.UUIDField(
        "Identifiant du commentaire", editable=False, max_length=32, blank=True,
        null=True)

    attachment_id = models.UUIDField(
        "Identifiant de la pièce jointe", editable=False, max_length=32,
        blank=True, null=True)

    object_type = models.CharField(
        "Type de l'objet lié", choices=EXTENDED_RELATED_MODELS, max_length=100)

    event_type = models.CharField(
        "Type de l'évènement", choices=EVENT_TYPES, max_length=100)

    project_slug = models.SlugField('Slug du projet', max_length=256, blank=True, null=True)

    feature_type_slug = models.SlugField(
        'Slug du type de signalement', max_length=256, blank=True, null=True)

    data = JSONField(blank=True, null=True)

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, verbose_name="Utilisateur", blank=True,
        null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Évènement"
        verbose_name_plural = "Évènements"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_on = timezone.now()
        super().save(*args, **kwargs)

    @property
    def notify_users(self):
        pass


class Subscription(models.Model):

    created_on = models.DateTimeField(
        "Date de création de l'abonnement", blank=True, null=True)

    feature = models.ForeignKey(
        "collab.Feature", on_delete=models.SET_NULL,
        null=True, blank=True)

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

    events = models.ManyToManyField('collab.Event')

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


@receiver(models.signals.post_delete, sender=Project)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Supprime les fichiers image lors de la suppression d'une instance projet.
    """
    if instance.thumbnail:
        if os.path.isfile(instance.thumbnail.path):
            os.remove(instance.thumbnail.path)


@receiver(models.signals.pre_delete, sender=User)
def anonymize_comments(sender, instance, **kwargs):
    """
    On transfère les commentaires sur un utilisateur anonyme
    """
    for comment in instance.comments:
        anonymous, _ = sender.objects.get_or_create(username="anonymous")
        comment.author = anonymous
        comment.save()


@receiver(models.signals.post_delete, sender=Attachment)
def submission_delete(sender, instance, **kwargs):
    instance.attachment_file.delete()


@receiver(models.signals.post_save, sender=Event)
def stack_event_notification(sender, instance, created, **kwargs):
    """
        TODO@cbenhabib: ajout d'une commande django branchée a un cron
        qui itere sur la stack en attente de traitement et qui envoi les messages
        aux destinataires abonnés.
        On ferme ensuite la stack en indiquant l'état d'exécution de la commande.
    """
    if created and instance.feature_id:
        if settings.DEFAULT_SENDING_FREQUENCY != "instantly":
            StackedEvent = apps.get_model(app_label='collab', model_name="StackedEvent")
            stack, _ = StackedEvent.objects.get_or_create(
                sending_frequency=settings.DEFAULT_SENDING_FREQUENCY, state='pending')
            stack.events.add(instance)
            stack.save()

        else:
            instance.notify_users()


@receiver(models.signals.post_save, sender=FeatureLink)
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
def update_feature_dates(sender, instance, **kwargs):
    if instance.project:
        instance.archived_on = instance.created_on + timezone.timedelta(
            days=instance.project.archive_feature)
        instance.deletion_on = instance.created_on + timezone.timedelta(
            days=instance.project.delete_feature)


@receiver(models.signals.post_save, sender=FeatureType)
def slugify_feature_type(sender, instance, created, **kwargs):

    if created:
        instance.slug = slugify("{}-{}".format(instance.pk, instance.title))
        instance.save()


@receiver(models.signals.post_save, sender=Project)
def slugify_project(sender, instance, created, **kwargs):

    if created:
        instance.slug = slugify("{}-{}".format(instance.pk, instance.title))
        instance.save()


@receiver(models.signals.post_save, sender=Project)
def set_author_perms(sender, instance, created, **kwargs):
    # On ajoute la permission d'admin de projet au créateur
    if created:
        Authorization = apps.get_model(app_label='collab', model_name="Authorization")
        UserLevelPermission = apps.get_model(app_label='collab', model_name="UserLevelPermission")
        try:
            Authorization.objects.create(
                project=instance,
                user=instance.creator,
                level=UserLevelPermission.objects.get(rank=4)
            )
        except Exception as err:
            logger.error("Error on Authorization create: {}".format(str(err)))


# EVENT'S TRIGGERS

@receiver(models.signals.post_save, sender=Project)
def create_event_on_project_creation(sender, instance, created, **kwargs):
    if created:
        Event = apps.get_model(app_label='collab', model_name="Event")
        Event.objects.create(
            user=instance.creator,
            event_type='create',
            object_type='project',
            project_slug=instance.slug,
            data={}
        )


@receiver(models.signals.post_save, sender=Comment)
def create_event_on_comment_creation(sender, instance, created, **kwargs):
    if created:
        Event = apps.get_model(app_label='collab', model_name="Event")
        Event.objects.create(
            feature_id=instance.feature_id,
            comment_id=instance.id,
            event_type='create',
            object_type='comment',
            user=instance.author,
            project_slug=instance.project.slug,
            feature_type_slug=instance.feature_type_slug,
            data={}
        )
