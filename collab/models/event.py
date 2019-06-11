from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField


class Event(models.Model):

    EVENT_TYPES = (
        ('create', 'Création'),
        ('update_attachment', "Modification d'une pièce jointe"),
        ('update_loc', 'Modification de la localisation'),
        ('update_attrs', "Modification d’un attribut"),
        ('delete', 'Suppression'),
        ('update_status', "Changement de statut"),
    )

    OBJ_TYPES = (
        ('feature', 'Signalement'),
        ('comment', 'Commentaire'),
    )

    creation_date = models.DateTimeField("Date de l'évènement",
                                         auto_now_add=True)

    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name="Utilisateur",
                             on_delete=models.CASCADE)

    feature_id = models.UUIDField("Identifiant du signalement",
                                  editable=False, max_length=32)

    object_type = models.CharField("Type de l'objet lié",
                                   choices=OBJ_TYPES,
                                   max_length=100)

    event_type = models.CharField("Type de l'évènement",
                                  choices=EVENT_TYPES,
                                  max_length=100)

    project_slug = models.SlugField('Slug', max_length=128)

    data = JSONField()

    class Meta:
        verbose_name = "Évènement"
        verbose_name_plural = "Évènements"
