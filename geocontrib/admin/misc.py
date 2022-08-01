
import logging

from django.contrib.gis import admin
from django_admin_listfilter_dropdown.filters import DropdownFilter

from geocontrib.models import StackedEvent


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

admin.site.register(StackedEvent, StackedEventAdmin)
