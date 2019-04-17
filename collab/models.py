from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.html import format_html
from django.utils.text import slugify
from datetime import timedelta

STATUS = (
    ('0', 'Brouillon'),
    ('1', 'En attente de publication'),
    ('2', 'Publié'),
    ('3', 'Archivé'),
)

class CustomUser(AbstractUser):
    # add additional fields in here
    nickname = models.CharField('nickname', max_length=15, blank=True)

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name.upper())


# Create your models here.

# class Status(models.Model):
#
#     status = models.CharField('Status des signalements',
#                               choices=STATUS,
#                               max_length=1, default='0')
#
#     def __str__(self):
#         return '%s' % (STATUS[int(self.status)][1])
#
#     class Meta:
#         verbose_name = "Status"
#         verbose_name_plural = "Status"


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
    title = models.CharField('Titre', max_length=128, unique=True)
    slug = models.SlugField('Slug', max_length=128, unique=True)
    creation_date = models.DateTimeField("Date de création du projet",
                                          auto_now_add=True)
    description = models.TextField('Description', blank=True)
    # image = models.ImageField('Image', upload_to="", blank=True, null=True)
    icons_URL = models.URLField("URL de l'icône du projet", blank=True,
                                 null=True, max_length=1000)
    geom_type = models.CharField('Type de géométrie', choices=GEOM_TYPE,
                                 max_length=1, default='0')
    moderation = models.BooleanField('Modération', default=False)
    visi_feature = models.CharField('Visibilité des signalements publiés',
                                    choices=USER_TYPE,
                                    max_length=1, default='0')
    visi_archive = models.CharField('Visibilité des signalements archivés',
                                    choices=USER_TYPE_ARCHIVE,
                                    max_length=1, default='0')
    archive_feature = models.DurationField('Délai avant archivage', blank=True,
                                            null=True)
    delete_feature = models.DurationField('Délai avant suppression',
                                           blank=True, null=True)
    feature_type = JSONField('Type de signalements disponibles',
                             blank=True, null=True)

    def __str__(self):
        return self.title

    def thumbLink(self):
        return format_html('<img src="{url}" width=200 height=200/>',
                           url=self.icons_URL)

    thumbLink.allow_tags = True
    thumbLink.short_description = "Icône"

    def _get_unique_slug(self):
        slug = slugify(self.title)
        unique_slug = slug
        num = 1
        while Project.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save(*args, **kwargs)

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
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    creation_date = models.DateTimeField("Date de création de l'Abonnement",
                                         auto_now_add=True)
    modification_date = models.DateTimeField("Date de modifictaion de l'Abonnement",
                                         auto_now=True)

    class Meta:
        # un role par projet
        unique_together = (
            ('user', 'project'),
        )


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


class Comment(models.Model):

    creation_date = models.DateTimeField("Date de création du commentaire",
                                         auto_now_add=True)
    author = models.ForeignKey(CustomUser, verbose_name="Auteur",
                               on_delete=models.CASCADE,
                               help_text="Auteur du commentaire")
    feature_id = models.UUIDField("Identifiant du signalement",
                                  editable=False, max_length=32)
    comment = models.TextField('Commentaire', blank=True)

    project_slug = models.SlugField('Slug', max_length=128)

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"


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
        upload_to="",
        # validators=[] -> TO DO VALIDER L'extension + Taille du fichier
    )

    creation_date = models.DateTimeField("Date de création du commentaire",
                                      auto_now_add=True)
    author = models.ForeignKey(CustomUser, verbose_name="Auteur",
                               on_delete=models.CASCADE,
                               help_text="Auteur du commentaire")
    feature_id = models.UUIDField("Identifiant du signalement",
                                  editable=False, max_length=32, blank=True)
    comment = models.ForeignKey(Comment,
                                on_delete=models.CASCADE)

    info = models.TextField('Info', blank=True)

    project_slug = models.SlugField('Slug', max_length=128)


    def __str__(self):
        return self.titre

    class Meta:
        verbose_name = "Pièce Jointe"
        verbose_name_plural = "Pièces Jointes"


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
    user = models.ForeignKey(CustomUser, verbose_name="utilisateur",
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
