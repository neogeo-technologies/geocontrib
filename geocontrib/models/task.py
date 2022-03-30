from django.conf import settings
from django.contrib.gis.db import models


class ImportTask(models.Model):

    def import_path(instance, filename):
        user_id = 'anonymous'
        if hasattr(instance, 'user') and instance.user.pk:
            user_id = instance.user.pk
        return "user_{0}/import_geojson/{1}".format(user_id, filename)

    STATUS_CHOICES = (
        ("pending", "En attente"),
        ("processing", "En cours"),
        ("finished", "Terminé"),
        ("failed", "Échoué"),
    )

    created_on = models.DateTimeField("Date de création", null=True, blank=True)

    started_on = models.DateTimeField("Date de démarrage", null=True, blank=True)

    finished_on = models.DateTimeField("Date de fin de traîtement", null=True, blank=True)

    status = models.CharField(
        "Status d'avancement",
        choices=STATUS_CHOICES,
        default="pending",
        max_length=10,
    )

    project = models.ForeignKey("geocontrib.Project", on_delete=models.CASCADE)

    feature_type = models.ForeignKey("geocontrib.FeatureType", on_delete=models.CASCADE)

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        verbose_name="Utilisateur",
        on_delete=models.SET_NULL, null=True, blank=True)

    file = models.FileField(
        "Fichier Importé",
        upload_to=import_path,
        blank=True, null=True
    )

    infos = models.TextField(blank=True)

    class Meta:
        verbose_name = "Tâche d'import"
        verbose_name_plural = "Tâches d'import"
