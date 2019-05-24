from django.db import models
from collab.models.customuser import CustomUser


class Subscription(models.Model):

    creation_date = models.DateTimeField("Date de création de l'Abonnement",
                                          auto_now_add=True)
    user = models.ForeignKey(CustomUser, verbose_name="Utilisateur",
                             on_delete=models.CASCADE,
                             help_text="Utilisateur abonné")
    feature_id = models.UUIDField("Identifiant du signalement",
                                  editable=False, max_length=32)
    project_slug = models.SlugField('Slug', max_length=128)

    class Meta:
        verbose_name = "Abonnement"
        verbose_name_plural = "Abonnements"