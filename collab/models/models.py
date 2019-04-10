from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models
from datetime import timedelta


# Create your models here.
class Project(models.Model):
    GEOM_TYPE = (
        ('0', 'Point'),
        ('1', 'Ligne brisée'),
        ('2', 'Polygone')
    )
    USER_TYPE = (
        ('0', 'Contributeur'),
        ('1', 'Utilisateur connecté'),
        ('2', 'Utilisateur anonyme'),
    )
    USER_TYPE_ARCHIVE = (
        ('0', 'Administrateur'),
        ('1', 'Modérateur'),
        ('2', 'Contributeur'),
        ('3', 'Utilisateur connecté'),
        ('4', 'Utilisateur anonyme'),
    )
    # Admin prepopulated_fields = {"slug": ("titre",)}
    title = models.CharField('Titre', max_length=15, unique=True)
    slug = models.SlugField('Slug', max_length=15, unique=True)
    description = models.TextField('Description', max_length=500, blank=True)
    image = models.ImageField('Image', upload_to="", blank=True, null=True)
    geom_type = models.CharField('Type de géométrie', choices=GEOM_TYPE,
                                 max_length=1, default='0')
    moderation = models.BooleanField('Modération', default=False)
    visu_marker = models.CharField('Visibilité des marqueurs publiés',
                                        choices=USER_TYPE,
                                        max_length=1, default='0')
    visu_archive = models.CharField('Visibilité des marqueurs archivés',
                                    choices=USER_TYPE_ARCHIVE,
                                    max_length=1, default='0')
    archive_marker = models.DurationField('Délai avant archivage',
                                         default=timedelta(days=30), blank=True,
                                         null=True)
    delete_marker = models.DurationField('Délai avant suppression',
                                             default=timedelta(days=30),
                                             blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"


# class Layers(models.Model):
#  TODO
#     name = models.CharField('Nom', max_length=15)
#     project = models.ManyToManyField(Project)
#
#     class Meta:
#         verbose_name = "Couche"
#         verbose_name_plural = "Couches"


class Autorisation(models.Model):
    LEVEL = (
        ('0', 'Consultation'),
        ('1', "Contribution"),
        ('2', 'Modération'),
        ('3', "Administration"),
    )
    level = models.CharField("Niveau d'autorisation",
                             choices=LEVEL,
                             max_length=1)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    project = models.OneToOneField(Project, on_delete=models.CASCADE)


class Subscription(models.Model):

    date_creation = models.DateTimeField("Date de création de l'Abonnement",
                                      auto_now_add=True)
    user = models.ForeignKey(User, verbose_name="Utilisateur",
                             on_delete=models.CASCADE,
                             help_text="Utilisateur abonné")
    marker_id = models.CharField("Identifiant du marqueur",
                                      max_length=32)

    class Meta:
        verbose_name = "Abonnement"
        verbose_name_plural = "Abonnements"


class Attachment(models.Model):

    TYPE_OBJET = (
        ('0', 'Signalement'),
        ('1', 'Commentaire'),
    )

    title = models.CharField('Titre', max_length=15)

    type_objet = models.CharField("Type d'objet concerné",
                                  choices=TYPE_OBJET,
                                  max_length=1)
    file = models.FileField(
        'Piece jointe',
        upload_to="",
        # validators=[] -> TO DO VALIDER L'extension + Taille du fichier
    )

    date_creation = models.DateTimeField("Date de création du commentaire",
                                      auto_now_add=True)
    author = models.ForeignKey(User, verbose_name="Auteur",
                               on_delete=models.CASCADE,
                               help_text="Auteur du commentaire")
    marker_id = models.CharField("Identifiant du marqueur",
                                      max_length=32, blank=True)

    info = models.TextField('Info', max_length=500, blank=True)

    # piece_jointe = TO DO
    def __str__(self):
        return self.titre

    class Meta:
        verbose_name = "Pièce Jointe"
        verbose_name_plural = "Pièces Jointes"


class Comment(models.Model):

    date_creation = models.DateTimeField("Date de création du commentaire",
                                      auto_now_add=True)
    author = models.ForeignKey(User, verbose_name="Auteur",
                               on_delete=models.CASCADE,
                               help_text="Auteur du commentaire")
    marker_id = models.CharField("Identifiant du signalement",
                                 max_length=32)
    comment = models.TextField('Commentaire', max_length=500, blank=True)

    attachment = models.OneToOneField(
            Attachment,
            on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"


class Event(models.Model):

    TYPE_EVENT = (
        ('0', 'Création'),
        ('1', "Modification d'une pièce jointe"),
        ('2', 'Modification de la localisation'),
        ('3', "Modification d’un attribut"),
        ('4', 'Suppression'),
        ('5', "Changement de statut"),
    )
    date_creation = models.DateTimeField("Date de l'évènement",
                                         auto_now_add=True)
    user = models.ForeignKey(User, verbose_name="utilisateur",
                             on_delete=models.CASCADE)
    marker_id = models.CharField("Identifiant du marqueur",
                                 max_length=32)
    type_object = models.CharField("Type d'évènement",
                                   choices=TYPE_EVENT,
                                   max_length=1)
    data = JSONField()

    class Meta:
        verbose_name = "Évènement"
        verbose_name_plural = "Évènements"
