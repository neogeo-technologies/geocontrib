from collab.choices import USER_TYPE
from collab.choices import USER_TYPE_ARCHIVE
from collab.choices import GEOM_TYPE
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.dispatch import receiver
from django.utils.html import format_html
from django.utils.text import slugify
APP_NAME = __package__.split('.')[0]


class Layer(models.Model):
    SCHEMAS = (
        ('wms', 'WMS'),
        ('tms', 'TMS')
    )
    name = models.CharField('Nom', max_length=256, blank=True, null=True)
    title = models.CharField('Titre', max_length=256, blank=True, null=True)
    style = models.CharField('Style', max_length=256, blank=True, null=True)
    service = models.URLField('Service')
    order = models.PositiveSmallIntegerField("Numéro d'ordre", default=0)
    schema_type = models.CharField(
        "Type de couche", choices=SCHEMAS, max_length=50, default="wms")
    project = models.ForeignKey('collab.Project', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Couche'
        verbose_name_plural = 'Couches'
        unique_together = ('project', 'order')

    def __str__(self):
        if self.title:
            return " ".format(self.pk, self.title)
        else:
            return "{}- {}".format(self.pk, self.service[0:25])


class Project(models.Model):

    # Admin prepopulated_fields = {"slug": ("titre",)}
    title = models.CharField('Titre', max_length=128, unique=True)
    slug = models.SlugField('Slug', max_length=128, unique=True)
    creation_date = models.DateTimeField("Date de création du projet",
                                          auto_now_add=True)
    description = models.TextField('Description', blank=True)
    illustration = models.ImageField('illustration', upload_to="illustrations", null=True)
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


    def __str__(self):
        return self.title

    def thumbLink(self):
        try:
            return format_html('<img src="{url}" width=200 height=200/>',
                               url=settings.BASE_URL+self.illustration.url)
        except Exception as e:
            pass

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

    def get_labels(self, feature_slug):
        """Get feature labels"""
        try:
            wording = FeatureType.objects.get(feature_type_slug=feature_slug).wording
            return wording
        except Exception as e:
            return {}

    def get_geom(self, feature_slug):
        """
            Return the feature geometry for a type of feature
            @feature_slug feature slug
            @return type of geom
        """
        try:
            geom = FeatureType.objects.get(feature_type_slug=feature_slug).get_geom_type_display()
            return geom
        except Exception as e:
            return 'Not Defined'


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"


class FeatureType(models.Model):

    name = models.CharField("Nom", max_length=128)

    feature_type_slug = models.SlugField("Feature Slug", max_length=256, null=True, blank=True)

    geom_type = models.CharField(
        "Type de champs géometrique", choices=GEOM_TYPE, max_length=50,
        default="0", null=True, blank=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    wording = JSONField('Libelle du type de signalement',
                         blank=True, null=True)

    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Type de signalement"
        verbose_name_plural = "Types de signalements"


class FeatureLink(models.Model):
    REL_TYPES = (
        ('doublon', 'Doublon'),
        ('remplace', 'Remplace'),
        ('est_remplace_par', 'Est remplacé par'),
        ('depend_de', 'Dépend de'),
    )
    relation_type = models.CharField(
        'Type de liaison', choices=REL_TYPES, max_length=50, default='doublon')
    feature_from = models.UUIDField(
        "Identifiant du signalement source", max_length=32, blank=True, null=True)
    feature_to = models.UUIDField(
        "Identifiant du signalement lié", max_length=32, blank=True, null=True)

    class Meta:
        verbose_name = "Type de liaison"
        verbose_name_plural = "Types de liaison"


@receiver(models.signals.post_save, sender=FeatureLink)
def create_symetrical_relation(sender, instance, created, **kwargs):
    if created:
        if instance.relation_type in ['doublon' or 'depend_de']:
            recip = instance.relation_type
        else:
            recip = 'est_remplace_par' if (instance.relation_type == 'remplace') else 'remplace'
        # Creation des réciproques
        sender.objects.update_or_create(
            relation_type=recip,
            feature_from=instance.feature_to,
            feature_to=instance.feature_from)


@receiver(models.signals.post_delete, sender=FeatureLink)
def submission_delete(sender, instance, **kwargs):
    related = []
    if instance.relation_type in ['doublon' or 'depend_de']:
        recip = instance.relation_type
    else:
        recip = 'est_remplace_par' if (instance.relation_type == 'remplace') else 'remplace'
    related = sender.objects.filter(
        relation_type=recip,
        feature_from=instance.feature_to,
        feature_to=instance.feature_from
    )
    # Suppression des réciproques
    for instance in related:
        instance.delete()
