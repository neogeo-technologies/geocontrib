
import logging

from django.contrib.gis import admin
from django_admin_listfilter_dropdown.filters import DropdownFilter

from geocontrib.models import StackedEvent
"""
import directly from the file to avoid circular import and not from model/__init__.py
since there are imports into a model(annotation.py) from geocontrib/emails.py
which trigger import of NotificationModel before the model is fully registrated
fixed by removing the import from model/__init__.py
"""
from geocontrib.models.notification import NotificationModel


logger = logging.getLogger(__name__)


class StackedEventAdmin(admin.ModelAdmin):
    list_display = (
        'project_slug',
        'sending_frequency',
        'state',
    )
    list_filter = (
        ('project_slug', DropdownFilter),
        'sending_frequency',
        'state',
    )

class NotificationModelAdmin(admin.ModelAdmin):
    def get_fields(self, request, obj=None):
        # Always include these fields
        fields = ['subject', 'message']
        
        # Conditionally include 'notification_type'
        if obj and obj.template_name == 'Événements groupés':
            fields.append('notification_type')
        
        return fields

admin.site.register(StackedEvent, StackedEventAdmin)
admin.site.register(NotificationModel, NotificationModelAdmin)
