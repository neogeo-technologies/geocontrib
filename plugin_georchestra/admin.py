import logging

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.gis import admin
from django.core.management import call_command
from django.shortcuts import redirect
from django.urls import path

from geocontrib.admin import UserAdmin

logger = logging.getLogger(__name__)

User = get_user_model()

admin.site.unregister(User)
# admin.site.unregister(UserAdmin)


class ThisUserAdmin(UserAdmin):
    change_list_template = 'admin/plugin_georchestra/user_change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('sync-users/', self.sync_users_ldap_view, name='sync_users'),
        ]
        return my_urls + urls

    def sync_users_ldap_view(self, request):
        try:
            call_command('georchestra_user_sync')
        except Exception:
            logger.exception('Georchestra LDAP sync failed')
            messages.error(request, "La synchronization a échouée")
        else:
            messages.success(request, "La synchronization a réussi.")

        return redirect('admin:geocontrib_user_changelist')


admin.site.register(User, ThisUserAdmin)
