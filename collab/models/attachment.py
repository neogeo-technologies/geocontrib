from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from collab.models.comment import Comment
from collab.models.customuser import CustomUser
from collab.models.project import Project
import uuid


class Attachment(models.Model):

    OBJET_TYPE = (
        ('0', 'Signalement'),
        ('1', 'Commentaire'),
    )
    attachment_id = models.UUIDField(
        "Identifiant de la pièce jointe", primary_key=True, default=uuid.uuid4,
        editable=False)
    creation_date = models.DateTimeField("Date de création de la pièce jointe",
                                         auto_now_add=True)
    title = models.CharField('Titre', max_length=128)

    type_objet = models.CharField("Type d'objet concerné",
                                  choices=OBJET_TYPE,
                                  max_length=1)
    file = models.FileField(
        'Piece jointe',
        upload_to="piecejointe",
        # validators=[] -> TO DO VALIDER L'extension + Taille du fichier
    )

    feature_id = models.UUIDField("Identifiant du signalement", null=True,
                                  editable=False, max_length=32, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    info = models.TextField('Info', blank=True)
    author = models.ForeignKey(CustomUser, verbose_name="Auteur",
                               on_delete=models.PROTECT,
                               help_text="Auteur du commentaire")

    def __str__(self):
        if self.title:
            return self.title

    class Meta:
        verbose_name = "Pièce Jointe"
        verbose_name_plural = "Pièces Jointes"


@receiver(post_delete, sender=Attachment)
def submission_delete(sender, instance, **kwargs):
    instance.file.delete(False)
