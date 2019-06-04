from django.db import models
from collab.models.customuser import CustomUser
from django.contrib.postgres.fields import JSONField


class Event(models.Model):

    EVEN_TYPE = (
        ('0', 'Création'),
        ('1', "Modification d'une pièce jointe"),
        ('2', 'Modification de la localisation'),
        ('3', "Modification d’un attribut"),
        ('4', 'Suppression'),
        ('5', "Changement de statut"),
    )
    creation_date = models.DateTimeField("Date de l'évènement",
                                         auto_now_add=True)
    user = models.ForeignKey(CustomUser, verbose_name="Utilisateur",
                             on_delete=models.CASCADE)
    feature_id = models.UUIDField("Identifiant du signalement",
                                  editable=False, max_length=32)
    object_type = models.CharField("Type d'évènement",
                                   choices=EVEN_TYPE,
                                   max_length=1)
    project_slug = models.SlugField('Slug', max_length=128)
    data = JSONField()

    class Meta:
        verbose_name = "Évènement"
        verbose_name_plural = "Évènements"