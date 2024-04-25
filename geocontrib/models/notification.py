from django.contrib.gis.db import models

"""
Model to store notification mail templates
in order to allow the administrator to modify mail object and body header
The field notification_type determines if the notification should be sent globally or per project
"""
class NotificationModel(models.Model):

    template_name = models.CharField(
        'Nom du modèle de notification', max_length=255)

    subject = models.CharField(
        'Objet', max_length=255, blank=True, null=True)

    message = models.TextField(
        'Corps du message', blank=True, null=True)

    TYPE_CHOICES = (
        ("global", "Globale"),
        ("per_project", "Par projet"),
    )
    notification_type = models.CharField(
        'Type de notification', choices=TYPE_CHOICES, max_length=50,
        default='global')

    class Meta:
        verbose_name = "Modèle de notifications"
        verbose_name_plural = "Modèles de notifications"

    def __str__(self):
        return self.template_name