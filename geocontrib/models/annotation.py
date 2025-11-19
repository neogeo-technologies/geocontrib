import os
import uuid

from django.apps import apps
from django.conf import settings
from django.contrib.gis.db import models
from django.utils import timezone

from geocontrib import logger
from geocontrib.choices import RELATED_MODELS
from geocontrib.choices import EXTENDED_RELATED_MODELS
from geocontrib.choices import EVENT_TYPES
from geocontrib.choices import STATE_CHOICES
from geocontrib.choices import FREQUENCY_CHOICES
from geocontrib.choices import MODERATOR
from geocontrib.emails import notif_moderators_pending_features
from geocontrib.emails import notif_creator_published_feature
from geocontrib.emails import notif_users_groups_published_feature
from geocontrib.utils import get_feature_bbox


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
        # On ne check pas la pk car custom field
        # donc on passe par _state
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

    is_key_document = models.BooleanField("Document clé", default=False)

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

    data = models.JSONField(blank=True, null=True)

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
    def display_user(self):
        res = "Utilisateur supprimé"
        if self.user:
            res = self.user.get_full_name() or self.user.username
        return res

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
        Gère les différents cas d'envoi de notifications liés à un événement.
        """
        if self.object_type != 'feature':
            return

        Feature = apps.get_model(app_label='geocontrib', model_name='Feature')
        feature = Feature.objects.get(feature_id=self.feature_id)
        project = feature.project

        feature_status = self.data.get('feature_status', {})
        status_has_changed = feature_status.get('has_changed', False)
        new_status = feature_status.get('new_status', 'draft')

        if project.moderation and status_has_changed and new_status == 'pending':
            # 1. Notifier les modérateurs si le signalement passe en "pending"
            self._notify_moderators(feature, project)

        if status_has_changed and new_status == 'published':
            # 2. Notifier l'auteur si le signalement est publié
            self._notify_creator(feature, project)

            # 3. Notifier les groupes d'utilisateurs si le signalement est publié
            self._notify_user_groups(feature)

    def _notify_moderators(self, feature, project):
        """Envoie une notification aux modérateurs lorsqu'un signalement passe en 'pending'."""
        Authorization = apps.get_model(app_label='geocontrib', model_name='Authorization')
        UserLevelPermission = apps.get_model(app_label='geocontrib', model_name='UserLevelPermission')

        event_initiator = self.user
        moderateur_rank = UserLevelPermission.objects.get(user_type_id=MODERATOR).rank
        moderators_emails = Authorization.objects.filter(
            project=project,
            level__rank__gte=moderateur_rank,
            level__rank__lt=6  # Exclut le lecteur
        ).exclude(user=event_initiator).values_list('user__email', flat=True)

        context = {
            'feature': feature,
            'event_initiator': event_initiator,
            'application_name': settings.APPLICATION_NAME,
            'application_abstract': settings.APPLICATION_ABSTRACT,
        }

        try:
            notif_moderators_pending_features(emails=moderators_emails, context=context)
        except Exception:
            logger.exception('Event.ping_users._notify_moderators')

    def _notify_creator(self, feature, project):
        """Notifie l'auteur du signalement si son signalement est publié."""
        event_initiator = self.user
        if project.moderation and event_initiator != feature.creator:
            context = {
                'feature': feature,
                'event': self
            }
            try:
                notif_creator_published_feature(
                    emails=[feature.creator.email], context=context
                )
            except Exception:
                logger.exception('Event.ping_users._notify_creator')

    def _notify_user_groups(self, feature):
        """Notifie les membres des groupes d'utilisateurs si un signalement est publié."""
        CustomField = apps.get_model(app_label='geocontrib', model_name='CustomField')
        notif_custom_fields = CustomField.objects.filter(
            feature_type=feature.feature_type, field_type='notif_group'
        )

        if not notif_custom_fields or not feature.feature_data:
            return

        context = {
            'feature': feature,
            'feature_bbox': get_feature_bbox(feature, buffer_m=100, to_string=True),
            'event': self
        }

        UsersGroup = apps.get_model(app_label='geocontrib', model_name='UsersGroup')
        UserGroupMembership = apps.get_model(app_label='geocontrib', model_name='UserGroupMembership')

        groups = [
            feature.feature_data[field.name]
            for field in notif_custom_fields if field.name in feature.feature_data
        ]

        global_group = UsersGroup.objects.filter(is_global=True)
        if global_group.exists():
            groups.append(global_group.first().codename)

        for group_codename in groups:
            try:
                group = UsersGroup.objects.get(codename=group_codename)
                user_emails = [
                    membership.user.email
                    for membership in UserGroupMembership.objects.filter(group=group)
                    .exclude(user=self.user)
                    .select_related('user')
                ]
                context['group'] = group

                if user_emails:
                    notif_users_groups_published_feature(emails=user_emails, context=context)
            except UsersGroup.DoesNotExist:
                logger.exception(f'Group of users with codename {group_codename} does not exist')
            except Exception:
                logger.exception('Event.ping_users._notify_user_groups')


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
    
    # This boolean field determines if the StackedEvent should exclusively contain 'key document' object_type events.
    # When set to True, only 'key document' events are included in this stack, allowing for targeted notifications
    # and easier tracking of notification states for these specific events.
    only_key_document = models.BooleanField("Document clé uniquement", default=False)

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
