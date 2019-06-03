from django.db import models
from collab.models.customuser import CustomUser
from collab.models.project import Project


class Comment(models.Model):

    creation_date = models.DateTimeField("Date de création du commentaire",
                                         auto_now_add=True)
    author = models.ForeignKey(CustomUser, verbose_name="Auteur",
                               on_delete=models.PROTECT,
                               help_text="Auteur du commentaire")
    feature_id = models.UUIDField("Identifiant du signalement",
                                  editable=False, max_length=32)
    feature_slug = models.SlugField('Feature slug', max_length=128)
    comment = models.TextField('Commentaire', blank=True)

    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
