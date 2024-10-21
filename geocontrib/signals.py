from functools import wraps
import os

from django.apps import apps
from django.conf import settings
from django.contrib.gis.db import models
from django.core.management import call_command
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from geocontrib import logger


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


@receiver(models.signals.post_delete, sender='geocontrib.Project')
@disable_for_loaddata
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Supprime les fichiers image lors de la suppression d'une instance projet.
    Seulement s'ils ne sont pas attachés à un autre projet
    """
    if instance.thumbnail \
            and instance.thumbnail.name != 'default.png' \
            and sender.objects.filter(thumbnail=instance.thumbnail).count() < 2 \
            and os.path.isfile(instance.thumbnail.path):
        os.remove(instance.thumbnail.path)


@receiver(models.signals.pre_delete, sender=settings.AUTH_USER_MODEL)
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


@receiver(models.signals.pre_delete, sender='geocontrib.Attachment')
@disable_for_loaddata
def submission_delete(sender, instance, **kwargs):
    instance.attachment_file.delete()


@receiver(models.signals.post_save, sender='geocontrib.FeatureLink')
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


# @receiver(models.signals.post_delete, sender='geocontrib.FeatureLink')
# @disable_for_loaddata
# def delete_symetrical_relation(sender, instance, **kwargs):
#     related = []
#     if instance.relation_type in ['doublon', 'depend_de']:
#         recip = instance.relation_type
#     else:
#         recip = 'est_remplace_par' if (instance.relation_type == 'remplace') else 'remplace'
#     related = sender.objects.filter(
#         relation_type=recip,
#         feature_from=instance.feature_to,
#         feature_to=instance.feature_from
#     )
#     # Suppression des réciproques
#     for instance in related:
#         instance.delete()

@receiver(models.signals.post_delete, sender='geocontrib.CustomField')
@disable_for_loaddata
def delete_custom_field_in_sql_view(sender, instance, **kwargs):
    if instance:
        call_command('generate_sql_view',
            mode=settings.AUTOMATIC_VIEW_CREATION_MODE,
            view_name=settings.AUTOMATIC_VIEW_SCHEMA_NAME,
            feature_type_id=instance.feature_type_id
        )

@receiver(models.signals.post_save, sender='geocontrib.CustomField')
@disable_for_loaddata
def update_sql_view(sender, instance, created, **kwargs):
    if instance:
        breakpoint()
        call_command('generate_sql_view',
            mode=settings.AUTOMATIC_VIEW_CREATION_MODE,
            view_name=settings.AUTOMATIC_VIEW_SCHEMA_NAME,
            feature_type_id=instance.feature_type_id
        )

@receiver(models.signals.post_delete, sender='geocontrib.FeatureType')
@disable_for_loaddata
def delete_sql_view(sender, instance, **kwargs):
    if instance:
        call_command('generate_sql_view',
            mode=settings.AUTOMATIC_VIEW_CREATION_MODE,
            view_name=settings.AUTOMATIC_VIEW_SCHEMA_NAME,
            feature_type_id=instance.id,
            is_deletion=True
        
        )

@receiver(models.signals.post_save, sender='geocontrib.FeatureType')
@disable_for_loaddata
def create_or_update_sql_view(sender, instance, created, **kwargs):
    if instance:
        update_fields = kwargs.get('update_fields', None)
        # if no field updated in feature_type, no need to update the view
        # changes could be inside customField forms, which already update the view from its own signal above
        if update_fields:
            call_command('generate_sql_view',
                mode=settings.AUTOMATIC_VIEW_CREATION_MODE,
                view_name=settings.AUTOMATIC_VIEW_SCHEMA_NAME,
                feature_type_id=instance.id
            )

@receiver(models.signals.post_save, sender='geocontrib.FeatureType')
@disable_for_loaddata
def slugify_feature_type(sender, instance, created, **kwargs):
    if created:
        instance.slug = slugify("{}-{}".format(instance.pk, instance.title))
        instance.save()


@receiver(models.signals.post_save, sender='geocontrib.Project')
@disable_for_loaddata
def slugify_project(sender, instance, created, **kwargs):

    if created:
        instance.slug = slugify("{}-{}".format(instance.pk, instance.title))
        instance.save()


@receiver(models.signals.post_save, sender='geocontrib.Project')
@disable_for_loaddata
def set_users_perms(sender, instance, created, **kwargs):
    # On ajoute la permission d'admin de projet au créateur
    if created:
        Authorization = apps.get_model(app_label='geocontrib', model_name="Authorization")
        UserLevelPermission = apps.get_model(
            app_label='geocontrib', model_name="UserLevelPermission")
        User = apps.get_model(app_label='geocontrib', model_name="User")
        try:
            Authorization.objects.create(
                project=instance,
                user=instance.creator,
                level=UserLevelPermission.objects.get(rank=5)
            )
        except Exception:
            logger.exception('Trigger.set_users_perms')
        """
        On ajoute la permission d'utilisateur connecté pour le projet à tous les autres utilisateurs actifs.
        Pour éviter que le traitement des autorisations avec beaucoup d'utiliseurs ne prennent trop de temps
        et déclenche une erreur 502 à cause d'un timeout, on utilise un bulk create pour faire une transitions unique
        Il n'y a pas d'équivalent de create_or_update et je n'ai pas trouvé le moyen d'exclure les autorisation déjà existante
        sur un projet pour un utilisateur, mais comme l'opération n'est effectué qu'au create du projet, il ne devrait pas
        y avoir ce type d'erreur. En cas d'erreurs, la bdd ne devrait pas être polluée en utilisant une transaction.atomic,
        car aucune opération n'est effectué sur la bdd en présence d'une erreur.
        """
        try:
            active_users = (
                User.objects
                .filter(is_active=True)
                .exclude(pk=instance.creator.pk)
            )
            default_permission_level = UserLevelPermission.objects.get(rank=1)

            new_authorizations = []
            for user in active_users:
                new_authorizations.append(Authorization(
                    project_id=instance.pk,
                    user_id=user.pk,
                    level=default_permission_level,
                    created_on = timezone.now(),
                    updated_on = timezone.now()
                ))

            with transaction.atomic():
                Authorization.objects.bulk_create(new_authorizations)

        except Exception:
            logger.exception('Trigger.set_users_perms')


@receiver(models.signals.post_save, sender=settings.AUTH_USER_MODEL)
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

@receiver(models.signals.post_save, sender='geocontrib.Project')
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


def setUser(user):
    user = user._wrapped if hasattr(user,'_wrapped') else user
    return user


@receiver(models.signals.post_save, sender='geocontrib.Feature')
@disable_for_loaddata
def create_event_on_feature_create_or_update(sender, instance, created, **kwargs):
    # Pour la modification ou la suppression d'un signalement l'évènement est generé parallelement
    # à l'update() afin de récupérer l'utilisateur courant.
    # Le signalement peut etre en 'pending' dés la création
    # on force le has_changed pour event.ping_users()
    Event = apps.get_model(app_label='geocontrib', model_name="Event")
    if created:
        Event.objects.create(
            feature_id=instance.feature_id,
            event_type='create',
            object_type='feature',
            user=instance.creator,
            project_slug=instance.project.slug,
            feature_type_slug=instance.feature_type.slug,
            data={
                'extra': instance.feature_data,
                'feature_title': instance.title,
                'feature_status': {
                    'has_changed': True,
                    'new_status': instance.status
                }
            }
        )
    elif instance:
        last_editor = setUser(instance.last_editor)
        Event.objects.create(
            feature_id=instance.feature_id,
            # If deletion_on is set, the feature has been deleted
            event_type='update' if instance.deletion_on == None else 'delete',
            object_type='feature',
            user= last_editor,
            project_slug=instance.project.slug,
            feature_type_slug=instance.feature_type.slug,
            data={
                'extra': instance.feature_data,
                'feature_title': instance.title,
                'feature_status': {
                    'has_changed': True,
                    'new_status': instance.status
                }
            }
        )


@receiver(models.signals.post_save, sender='geocontrib.Comment')
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


@receiver(models.signals.post_save, sender='geocontrib.Attachment')
@disable_for_loaddata
def create_event_on_attachment_creation(sender, instance, created, **kwargs):
    """
    Creates an event whenever a new attachment is saved to the database.
    This function checks if the attachment is either not linked to a comment 
    (as events linked to comments notify subscribers with a global notification), 
    or is marked as a key document, to send a specific notification for 'key_document' events.

    Args:
        sender (Model): The model class that sent the signal.
        instance (Attachment): The actual instance of Attachment being saved.
        created (bool): True if a new record was created, indicating this is a new attachment.
        **kwargs: Additional keyword arguments supplied by the signal.
    """
    Event = apps.get_model(app_label='geocontrib', model_name="Event")
    # Check if the attachment is newly created and either not related to a comment or is a key document
    if created and (not instance.comment or instance.is_key_document):
        # Create a new event in the database
        Event.objects.create(
            feature_id=instance.feature_id,  # Link the event to the same feature as the attachment
            attachment_id=instance.id,  # Record the ID of the new attachment
            event_type='create',  # Define the type of event
            object_type='key_document' if instance.is_key_document else 'attachment',  # Determine the object type based on whether it's a key document
            user=instance.author,  # Associate the event with the user who created the attachment
            project_slug=instance.project.slug,  # Include the project slug for further filtering
            data={}  # Empty dictionary for additional data, can be used for extending features
        )


@receiver(models.signals.post_save, sender='geocontrib.Event')
@disable_for_loaddata
def notify_or_stack_events(sender, instance, created, **kwargs):
    """
    This signal handler either stacks new events for batch notifications or notifies users immediately,
    depending on the configured notification frequency. It specifically handles 'key_document' events separately
    by creating or updating a StackedEvent instance dedicated to key documents.

    Args:
        sender (Model): The model class that sent the signal.
        instance (Event): The actual instance being saved.
        created (bool): True if a new record was created.
        **kwargs: Additional keyword arguments.
    """
    # Process only newly created events that have a related project and when notifications are not set to 'never'
    if created and instance.project_slug and settings.DEFAULT_SENDING_FREQUENCY != 'never':
        # Events are stacked based on the sending frequency setting to notify subscribers later
        StackedEvent = apps.get_model(app_label='geocontrib', model_name="StackedEvent")
        
        # Determine the stack type based on the object_type of the event
        is_key_document = instance.object_type == 'key_document'
        
        try:
            # Get or create a pending StackedEvent specific to the event type (key_document or general)
            stack, _ = StackedEvent.objects.get_or_create(
                sending_frequency=settings.DEFAULT_SENDING_FREQUENCY,
                state='pending',
                project_slug=instance.project_slug,
                only_key_document=is_key_document  # Use the model field to segregate events
            )
        except Exception as e:
            logger.exception(e)
            # Log a warning if multiple stacked events exist, suggesting to remove duplicates
            logger.warning("Several StackedEvent exists with sending_frequency='%s', state='pending', project_slug='%s', only_key_document='%s', remove one",
                           settings.DEFAULT_SENDING_FREQUENCY, instance.project_slug, is_key_document)
            # Retrieve the first pending stack if get_or_create fails due to duplicates
            stack = StackedEvent.objects.filter(
                sending_frequency=settings.DEFAULT_SENDING_FREQUENCY,
                state='pending',
                project_slug=instance.project_slug,
                only_key_document=is_key_document
            ).first()

        # Add the event instance to the stack and save the stack
        stack.events.add(instance)
        stack.save()

        # Notify collaborators of messages requiring immediate action
        try:
            instance.ping_users()
        except Exception:
            # Log an exception if there is an error during the ping users operation
            logger.exception('ping_users@notify_or_stack_events')


# Si besoin d'obliger un seul queryable à True
# @receiver(models.signals.post_save, sender='geocontrib.ContextLayer')
# @disable_for_loaddata
# def queryable_layers_unique(sender, instance, created, **kwargs):
#     if instance.queryable:
#         sender.objects.filter(
#             base_map=instance.base_map, queryable=True
#         ).exclude(
#             pk=instance.pk
#         ).update(queryable=False)
