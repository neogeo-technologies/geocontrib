import uuid
from django.db import models
from collab.models.customuser import CustomUser
from collab.models.project import Project


class Comment(models.Model):

    comment_id = models.UUIDField(
        "Identifiant du commentaire", primary_key=True, default=uuid.uuid4,
        editable=False)

    comment = models.TextField('Commentaire', blank=True)

    creation_date = models.DateTimeField(
        "Date de création du commentaire", auto_now_add=True)

    feature_id = models.UUIDField(
        "Identifiant du signalement", editable=False, max_length=32)

    feature_type_slug = models.SlugField('Slug du type de signalement', max_length=128)

    author = models.ForeignKey(
        CustomUser, verbose_name="Auteur", on_delete=models.PROTECT,
        help_text="Auteur du commentaire")

    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
