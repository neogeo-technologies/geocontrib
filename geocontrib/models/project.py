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
    attributes = models.ManyToManyField('ProjectAttribute', through='ProjectAttributeAssociation', verbose_name="Attributs")

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
    """
    Represents a customizable attribute for a project within the application. Each attribute
    can have a specific type (e.g., boolean, list, multi-choice list), along with options for
    list-based types and a default value. When a new ProjectAttribute is created, it updates
    existing projects to associate them with this new attribute and its default value.
    """
    
    label = models.CharField("Label", max_length=256, null=False, blank=False)
    name = models.CharField("Nom", max_length=128, null=False, blank=False)
    field_type = models.CharField(
        "Type de champ", choices=(
            ("boolean", "Booléen"),
            ("list", "Liste de valeurs"),
            ("multi_choices_list", "Liste à choix multiples")),
        max_length=50, default="boolean"
    )
    options = ArrayField(base_field=models.CharField(max_length=256), null=True, blank=True)

    default_value = models.CharField("Valeur par défaut", max_length=50, null=True, blank=True)

    display_filter = models.BooleanField("Afficher un filtre sur la liste des projets", default=False)

    default_filter_enabled = models.BooleanField("Activer le filtre par défaut", default=False)

    default_filter_value = models.CharField("Valeur du filtre par défaut", max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = "Attribut projet"
        verbose_name_plural = "Attributs projet"

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to update existing projects with this attribute's
        default value when a new ProjectAttribute instance is created.
        """
        # Check if this is a new instance being created by looking for the absence of self._state.adding.
        is_new = self._state.adding
        # Call the superclass's save method to ensure the instance is saved.
        super(ProjectAttribute, self).save(*args, **kwargs)

        # If this is a new instance and a default value is set, update existing projects.
        if is_new and self.default_value:
            self.update_projects_with_default()

    def update_projects_with_default(self):
        """
        Updates all existing projects by associating them with this attribute and its default value,
        creating a new ProjectAttributeAssociation if one does not already exist.
        """
        # Fetch all existing projects from the database.
        projects = Project.objects.all()

        for project in projects:
            # For each project, create an association with this attribute and its default value,
            # if such an association does not already exist.
            ProjectAttributeAssociation.objects.get_or_create(
                project=project,
                attribute=self,
                defaults={'value': self.default_value}
            )

    def __str__(self):
        """
        String representation of the ProjectAttribute instance, displaying its label.
        """
        return self.label

class ProjectAttributeAssociation(models.Model):
    """
    Represents an association between a Project and a ProjectAttribute, storing the value of the attribute for a specific project.
    This model ensures that each combination of project and attribute is unique.

    Attributes:
        project (ForeignKey): A reference to the Project model. This field defines a many-to-one relationship, indicating that each association is linked to a specific project.
        attribute (ForeignKey): A reference to the ProjectAttribute model, stored in the database under the 'attribute_id' column. It represents the attribute associated with the project.
        value (CharField): Stores the value of the attribute for the specified project. This can be any string that the attribute is set to hold.
    
    Meta:
        unique_together: Ensures that each project-attribute pair is unique within the database to prevent duplicate associations.
    """
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    attribute = models.ForeignKey('ProjectAttribute', on_delete=models.CASCADE, db_column='attribute_id')
    value = models.CharField("Valeur", max_length=256)

    class Meta:
        unique_together = ('project', 'attribute')
