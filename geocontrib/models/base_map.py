from django.contrib.gis.db import models
# from django.contrib.postgres.fields import JSONField
from django.core.validators import MaxValueValidator, MinValueValidator

from geocontrib.managers import LayerManager


class BaseMap(models.Model):
    title = models.CharField('Titre', max_length=256, blank=True, null=True)

    project = models.ForeignKey('geocontrib.Project', on_delete=models.CASCADE)

    layers = models.ManyToManyField('geocontrib.Layer', through='ContextLayer')

    class Meta:
        verbose_name = 'Fond cartographique'
        verbose_name_plural = 'Fonds cartographiques'

    def __str__(self):
        title = self.title or 'N/A'
        return "{0} - ({1})".format(title, self.project)


class ContextLayer(models.Model):

    order = models.PositiveSmallIntegerField("Numéro d'ordre", default=0)

    opacity = models.DecimalField(
        "Opacité",
        max_digits=3,
        decimal_places=2,
        validators=[
            MaxValueValidator(1),
            MinValueValidator(0)
        ],
        default=1)

    queryable = models.BooleanField("Requêtable", default=False)

    base_map = models.ForeignKey(
        verbose_name="Fond cartographique", to='geocontrib.BaseMap', on_delete=models.CASCADE)

    layer = models.ForeignKey(
        verbose_name="Couche", to='geocontrib.Layer', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Liaison Fond-Couche'
        verbose_name_plural = 'Liaison Fond-Couche'
        ordering = ('order', )
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['base_map', ],
        #         condition=models.Q(queryable=True),
        #         name='unique_queryable_base_map')
        # ]


class Layer(models.Model):
    SCHEMAS = (
        ('wms', 'WMS'),
        ('tms', 'TMS')
    )

    title = models.CharField('Titre', max_length=256, blank=True, null=True)

    service = models.CharField('Service', max_length=256)

    schema_type = models.CharField(
        "Type de couche", choices=SCHEMAS, max_length=50, default="wms")

    options = models.JSONField("Options", blank=True, null=True)

    objects = models.Manager()

    handy = LayerManager()

    class Meta:
        verbose_name = 'Couche'
        verbose_name_plural = 'Couches'

    def __str__(self):
        title = self.title or ''
        return "{0} - {1} ({2})".format(title, self.service, self.schema_type)
