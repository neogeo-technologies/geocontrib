import uuid

from django.apps import apps
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
# from django.db.models.JSONField import JSONField
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property

from rest_framework_mvt.managers import MVTManager

from geocontrib.choices import TYPE_CHOICES
from geocontrib.managers import AvailableFeaturesManager
from geocontrib.managers import FeatureLinkManager


class Feature(models.Model):

    STATUS_CHOICES = (
        ("draft", "Brouillon"),
        ("pending", "En attente de publication"),
        ("published", "Publié"),
        ("archived", "Archivé"),
    )

    feature_id = models.UUIDField(
        "Identifiant", primary_key=True, editable=False, default=uuid.uuid4)

    title = models.CharField("Titre", max_length=128, null=True, blank=True)

    description = models.TextField("Description", blank=True, null=True)

    status = models.CharField(
        "Statut", choices=STATUS_CHOICES, max_length=50,
        default="draft")

    created_on = models.DateTimeField("Date de création", null=True, blank=True)

    updated_on = models.DateTimeField("Date de maj", null=True, blank=True)

    archived_on = models.DateField(
        "Date d'archivage automatique", null=True, blank=True)

    deletion_on = models.DateField(
        "Date de suppression automatique", null=True, blank=True)

    creator = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, verbose_name="Créateur",
        on_delete=models.SET_NULL, related_name='features', null=True, blank=True)

    last_editor = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, verbose_name="Dernier éditeur",
        on_delete=models.SET_NULL, related_name='edited_features', null=True, blank=True)

    project = models.ForeignKey("geocontrib.Project", on_delete=models.CASCADE)

    feature_type = models.ForeignKey("geocontrib.FeatureType", on_delete=models.CASCADE)

    geom = models.GeometryField("Géométrie", srid=4326)

    feature_data = models.JSONField(blank=True, null=True)

    objects = models.Manager()

    handy = AvailableFeaturesManager()

    vector_tiles = MVTManager()

    class Meta:
        verbose_name = "Signalement"
        verbose_name_plural = "Signalements"

    def clean(self):
        if self.feature_data and not isinstance(self.feature_data, dict):
            raise ValidationError('Format de donnée invalide')

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.created_on = timezone.now()
            self.last_editor = self.creator
        self.updated_on = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):

        return reverse('geocontrib:feature_update', kwargs={
            'slug': self.project.slug, 'feature_type_slug': self.feature_type.slug,
            'feature_id': self.feature_id})

    def get_view_url(self):

        return reverse('geocontrib:feature_detail', kwargs={
            'slug': self.project.slug, 'feature_type_slug': self.feature_type.slug,
            'feature_id': self.feature_id})

    def change_status(self, status):
        self.status = status
        self.save()

    @property
    def custom_fields_as_list(self):
        CustomField = apps.get_model(app_label='geocontrib', model_name="CustomField")
        custom_fields = CustomField.objects.filter(feature_type=self.feature_type)
        res = []
        if custom_fields.exists():
            for row in custom_fields.order_by('position').values('name', 'label', 'field_type'):
                value = ''
                if isinstance(self.feature_data, dict):
                    value = self.feature_data.get(row['name'])
                res.append({
                    'label': row['label'],
                    'field_type': row['field_type'],
                    'value': value
                })
        return res

    @property
    def display_creator(self):
        res = "Utilisateur supprimé"
        if self.creator:
            res = self.creator.get_full_name() or self.creator.username
        return res

    @property
    def display_last_editor(self):
        res = "Utilisateur supprimé"
        if self.last_editor:
            res = self.last_editor.get_full_name() or self.last_editor.username
        return res

    @cached_property
    def color(self):
        color = self.feature_type.color
        if self.feature_data and self.feature_type.colors_style:
            custom_field_name = self.feature_type.colors_style.get('custom_field_name', '')
            value = self.feature_data.get(custom_field_name)
            color = self.feature_type.colors_style.get('colors', {}).get(value)
            if not color:
                color = self.feature_type.color
        return color


class FeatureLink(models.Model):
    REL_TYPES = (
        ('doublon', 'Doublon'),
        ('remplace', 'Remplace'),
        ('est_remplace_par', 'Est remplacé par'),
        ('depend_de', 'Dépend de'),
    )

    relation_type = models.CharField(
        'Type de liaison', choices=REL_TYPES, max_length=50, default='doublon')

    feature_from = models.ForeignKey(
        "geocontrib.Feature", verbose_name="Signalement source",
        on_delete=models.CASCADE, related_name='feature_from', db_column='feature_from')

    feature_to = models.ForeignKey(
        "geocontrib.Feature", verbose_name="Signalement lié",
        on_delete=models.CASCADE, related_name='feature_to', db_column='feature_to')

    objects = models.Manager()

    handy = FeatureLinkManager()

    class Meta:
        verbose_name = "Liaison entre signalements"
        verbose_name_plural = "Liaisons entre signalements"

    def update_relations(self, relation_type):
        new_relation = relation_type
        if new_relation in ['doublon', 'depend_de']:
            recip = new_relation
        else:
            recip = 'est_remplace_par' if (new_relation == 'remplace') else 'remplace'
        # Maj des réciproques
        FeatureLink.objects.update_or_create(
            feature_from=self.feature_to, feature_to=self.feature_from,
            defaults={'relation_type': recip}
        )
        self.relation_type = new_relation
        self.save(update_fields=['relation_type', ])


class FeatureType(models.Model):

    GEOM_CHOICES = (
        ("linestring", "Ligne"),
        ("point", "Point"),
        ("polygon", "Polygone"),
    )

    title = models.CharField("Titre", max_length=128)

    title_optional = models.BooleanField("Titre optionnel", default=False)

    slug = models.SlugField("Slug", max_length=256, editable=False, null=True)

    geom_type = models.CharField(
        "Type de géométrie", choices=GEOM_CHOICES, max_length=50,
        default="point")

    color = models.CharField(
        verbose_name='Couleur', max_length=7, blank=True, null=True
    )

    icon = models.CharField(
        verbose_name='Icône', max_length=128, blank=True, null=True
    )

    colors_style = models.JSONField(
        "Style Champs coloré", blank=True, null=True
    )

    project = models.ForeignKey(
        "geocontrib.Project", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Type de signalement"
        verbose_name_plural = "Types de signalements"

    def clean(self):
        if self.colors_style:
            if not isinstance(self.colors_style, dict):
                raise ValidationError('Format de donnée invalide')

    def save(self, *args, **kwargs):
        if not self.pk and self.title:
            self.created_on = timezone.now()
        self.updated_on = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def is_editable(self):
        Feature = apps.get_model(app_label='geocontrib', model_name="Feature")
        return not Feature.objects.filter(feature_type=self).exists()

# class CustomFieldInterface(models.Model):
#
#     INTERFACE_CHOICES = (
#         ("unique", "Entrée unique"),
#         ("multi_choice", "Choix multiple"),
#         ("radio", "Bouton radio"),
#         ("range", "Curseur"),
#     )
#
#     interface_type = models.CharField(
#         "Type d'interface", choices=INTERFACE_CHOICES, max_length=50,
#         default="unique", null=True, blank=True)
#
#     # Permet de stocker les options des differents type d'input
#     options = ArrayField(base_field=models.CharField(max_length=256), blank=True)
#
#     class Meta:
#         verbose_name = "Interface de champ personnalisé"
#         verbose_name_plural = "Interfaces de champs personnalisés"


class CustomField(models.Model):
    label = models.CharField("Label", max_length=128, null=True, blank=True)

    name = models.CharField("Nom", max_length=128, null=True, blank=True)

    position = models.PositiveSmallIntegerField(
        "Position", default=0, blank=False, null=False)

    field_type = models.CharField(
        "Type de champ", choices=TYPE_CHOICES, max_length=50,
        default="boolean", null=False, blank=False)

    feature_type = models.ForeignKey(
        "geocontrib.FeatureType", on_delete=models.CASCADE
    )

    options = ArrayField(
        base_field=models.CharField(max_length=256), null=True, blank=True)

    # interface = models.ForeignKey(
    #     "geocontrib.CustomFieldInterface", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "Champ personnalisé"
        verbose_name_plural = "Champs personnalisés"
        unique_together = (('name', 'feature_type'),)

    def __str__(self):
        return "{}.{}".format(self.feature_type.slug, self.name)

    def clean(self):

        if self.field_type == 'list' and len(self.options) == 0:
            raise ValidationError("La liste d'options ne peut être vide. ")
