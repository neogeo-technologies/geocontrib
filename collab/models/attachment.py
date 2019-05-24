from django.db import models
from collab.models.comment import Comment
from collab.models.project import Project


class Attachment(models.Model):

    OBJET_TYPE = (
        ('0', 'Signalement'),
        ('1', 'Commentaire'),
    )

    title = models.CharField('Titre', max_length=128)

    type_objet = models.CharField("Type d'objet concerné",
                                  choices=OBJET_TYPE,
                                  max_length=1)
    file = models.FileField(
        'Piece jointe',
        upload_to="piecejointe",
        # validators=[] -> TO DO VALIDER L'extension + Taille du fichier
    )

    feature_id = models.UUIDField("Identifiant du signalement",
                                  editable=False, max_length=32, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)
    info = models.TextField('Info', blank=True)

    def __str__(self):
        return self.titre

    class Meta:
        verbose_name = "Pièce Jointe"
        verbose_name_plural = "Pièces Jointes"