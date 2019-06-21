from django.db import models
from collab.models.customuser import CustomUser
from collab.utils import handle_email


class Subscription(models.Model):

    creation_date = models.DateTimeField("Date de création de l'Abonnement",
                                          auto_now_add=True)
    feature_id = models.UUIDField("Identifiant du signalement",
                                  editable=False, max_length=32)
    project_slug = models.SlugField('Slug', max_length=128)

    users = models.ManyToManyField(
        CustomUser, verbose_name="Utilisateurs", help_text="Utilisateurs abonnés")

    class Meta:
        verbose_name = "Abonnement"
        verbose_name_plural = "Abonnements"

    @classmethod
    def notify(cls, **defaults):
        """
        TODO@cbenhabib: mettre des controles sur le contenu de context
        """

        context = defaults.pop('context', None)
        if context:
            try:
                users_pk = cls.objects.filter(**defaults).values_list('users__pk', flat=True)
            except Exception as err:
                print(err)
                pass
            else:
                handle_email(CustomUser.objects.filter(pk__in=users_pk), context)
