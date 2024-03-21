from functools import wraps
import os

from django.apps import apps
from django.conf import settings
from django.contrib.gis.db import models
from django.dispatch import receiver
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
        try:
            for user in User.objects.filter(is_active=True).exclude(pk=instance.creator.pk):
                Authorization.objects.update_or_create(
                    project=instance,
                    user=user,
                    defaults={'level': UserLevelPermission.objects.get(rank=1)}
                )
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
    # Pour la modification d'un signalement l'évènement est generé parallelement
    # à l'update() afin de recupere l'utilisateur courant.
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
    else:
        if instance:
            last_editor = setUser(instance.last_editor)
            Event.objects.create(
                feature_id=instance.feature_id,
                event_type='update',
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


@receiver(models.signals.post_save, sender='geocontrib.Event')
@disable_for_loaddata
def notify_or_stack_events(sender, instance, created, **kwargs):

    if created and instance.project_slug and settings.DEFAULT_SENDING_FREQUENCY != 'never':
        # On empile les evenements pour notifier les abonnés, en fonction de la fréquence d'envoi
        StackedEvent = apps.get_model(app_label='geocontrib', model_name="StackedEvent")
        try:
            stack, _ = StackedEvent.objects.get_or_create(
                sending_frequency=settings.DEFAULT_SENDING_FREQUENCY, state='pending',
                project_slug=instance.project_slug)
        except Exception as e:
            logger.exception(e)
            logger.warning("Several StackedEvent exists with sending_frequency='%s',"
                           " state='pending', project_slug='%s', remove one",
                           settings.DEFAULT_SENDING_FREQUENCY,
                           instance.project_slug)
            stack = StackedEvent.objects.filter(
                sending_frequency=settings.DEFAULT_SENDING_FREQUENCY,
                state='pending',
                project_slug=instance.project_slug).first()

        stack.events.add(instance)
        stack.save()

        # On notifie les collaborateurs des messages nécessitant une action immédiate
        try:
            instance.ping_users()
        except Exception:
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
