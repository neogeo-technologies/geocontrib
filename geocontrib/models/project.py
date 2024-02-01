from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.urls import reverse
from django.utils import timezone


class Project(models.Model):

    def thumbnail_dir(instance, filename):
        return "user_{0}/{1}".format(instance.creator.pk, filename)

    def limit_pub():
        return {"rank__lte": 2}

    def limit_arch():
        # TODO: n'a plus lieu d'etre, les signalements archivés pouvant
        # potentiellement etre visible par tous.
        return {"rank__lte": 4}

    title = models.CharField("Titre", max_length=128, unique=True)

    slug = models.SlugField("Slug", max_length=256, editable=False, null=True)

    created_on = models.DateTimeField("Date de création", blank=True, null=True)

    updated_on = models.DateTimeField("Date de modification", blank=True, null=True)

    description = models.TextField("Description", blank=True, null=True)

    moderation = models.BooleanField("Modération", default=False)

    thumbnail = models.ImageField("Illustration", upload_to=thumbnail_dir, default="default.png")

    creator = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, verbose_name="Créateur",
        on_delete=models.SET_NULL, null=True, blank=True)

    access_level_pub_feature = models.ForeignKey(
        to="geocontrib.UserLevelPermission", limit_choices_to=limit_pub,
        verbose_name="Visibilité des signalements publiés",
        on_delete=models.PROTECT,
        related_name="access_published"
    )

    access_level_arch_feature = models.ForeignKey(
        to="geocontrib.UserLevelPermission", limit_choices_to=limit_arch,
        verbose_name="Visibilité des signalements archivés",
        on_delete=models.PROTECT,
        related_name="access_archived"
    )

    archive_feature = models.PositiveIntegerField(
        "Délai avant archivage", blank=True, null=True)

    delete_feature = models.PositiveIntegerField(
        "Délai avant suppression", blank=True, null=True)

    map_max_zoom_level = models.PositiveIntegerField(
        "Niveau de zoom maximum de la carte", default=22)

    ldap_project_contrib_groups = ArrayField(
        verbose_name="Groupes LDAP des contributeurs et modérateurs",
        base_field=models.CharField(max_length=256), blank=True, null=True)

    ldap_project_admin_groups = ArrayField(
        verbose_name="Groupes LDAP des administrateurs",
        base_field=models.CharField(max_length=256), blank=True, null=True)

    is_project_type = models.BooleanField(
        "Est un projet type", default=False, blank=True)

    generate_share_link = models.BooleanField("Génération d'un lien de partage externe", default=False)

    fast_edition_mode = models.BooleanField("Mode d'édition rapide de signalements", default=False)

    feature_browsing_default_filter = models.CharField(
        verbose_name="Filtre par défaut du parcours du signalement",
        max_length=20,
        blank=True,
        default=""
    )
    feature_browsing_default_sort = models.CharField(
        verbose_name="Tri par défaut du parcours du signalement",
        max_length=20,
        default="-created_on"
    )

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ('title', )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_on = timezone.now()
        self.updated_on = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('geocontrib:project', kwargs={'slug': self.slug})

    def calculate_bbox(self):
        if self.feature_set.exists():
            bbox = self.feature_set.aggregate(models.Extent('geom'))['geom__extent']
            return bbox
        else:
            return None
        
class ProjectAttribute(models.Model):
    label = models.CharField("Label", max_length=256, null=False, blank=False)

    name = models.CharField("Nom", max_length=128, null=False, blank=False)

    field_type = models.CharField(
        "Type de champ", choices=(
            ("boolean", "Booléen"),
            ("list", "Liste de valeurs"),
            ("multi_choices_list", "Liste à choix multiples")),
        max_length=50, default="boolean"
    )

    options = ArrayField(
        base_field=models.CharField(max_length=256), null=True, blank=True
    )

    default_value = models.CharField(
        "Valeur par défaut",
        max_length=50, null=True, blank=True
    )

    class Meta:
        verbose_name = "Attribut projet"
        verbose_name_plural = "Attributs projet"