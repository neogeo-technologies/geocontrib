from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.apps import apps
from django.dispatch import receiver


class Event(models.Model):

    EVENT_TYPES = (
        ('create', "Création"),
        ('update_attachment', "Modification d'une pièce jointe"),
        ('update_loc', 'Modification de la localisation'),
        ('update_attrs', "Modification d’un attribut"),
        ('update_status', "Changement de statut"),
        ('delete', 'Suppression'),
    )

    OBJ_TYPES = (
        ('attachment', 'Pièce jointe'),
        ('comment', 'Commentaire'),
        ('feature', 'Signalement'),
        ('project', 'Projet'),
    )

    creation_date = models.DateTimeField("Date de l'évènement",
                                         auto_now_add=True)

    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name="Utilisateur",
                             blank=True, null=True,
                             on_delete=models.CASCADE)

    feature_id = models.UUIDField("Identifiant du signalement",
                                  editable=False, max_length=32,
                                  blank=True, null=True)

    comment_id = models.UUIDField("Identifiant du commentaire",
                                  editable=False, max_length=32,
                                  blank=True, null=True)
    attachment_id = models.UUIDField("Identifiant de la pièce jointe",
                                     editable=False, max_length=32,
                                     blank=True, null=True)

    object_type = models.CharField("Type de l'objet lié",
                                   choices=OBJ_TYPES,
                                   max_length=100)

    event_type = models.CharField("Type de l'évènement",
                                  choices=EVENT_TYPES,
                                  max_length=100)

    project_slug = models.SlugField('Slug Projet', max_length=256, blank=True, null=True)

    feature_type_slug = models.SlugField('Slug Feature', max_length=256, blank=True, null=True)

    data = JSONField(blank=True, null=True)

    class Meta:
        verbose_name = "Évènement"
        verbose_name_plural = "Évènements"


@receiver(models.signals.post_save, sender=Event)
def trigger_emails(sender, instance, created, **kwargs):

    if created and instance.feature_id:

        Subscription = apps.get_model(app_label='collab', model_name="Subscription")
        defaults = {
            "feature_id": str(instance.feature_id),
            "context": {
                "object_type": instance.get_object_type_display(),
                "event_type": instance.event_type,
                "identifiant": str(instance.feature_id),
                "url": "http://url-de-l-objet.collab.fr/{}".format(instance.feature_id)
            }
        }
        Subscription.notify(**defaults)
