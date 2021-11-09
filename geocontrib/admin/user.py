import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.gis import admin
from django.utils.translation import ugettext_lazy as _

from geocontrib.models import Authorization
from geocontrib.models import Subscription
from geocontrib.models import UserLevelPermission


logger = logging.getLogger(__name__)
User = get_user_model()


class UserAdmin(DjangoUserAdmin):
    list_display = (
        'username', 'last_name', 'first_name', 'email',
        'is_superuser', 'is_administrator', 'is_staff', 'is_active'
    )
    search_fields = ('id', 'username', 'first_name', 'last_name', 'email')
    ordering = ('last_name', 'first_name', 'username', )
    verbose_name_plural = 'utilisateurs'
    verbose_name = 'utilisateur'

    readonly_fields = (
        'id',
        'date_joined',
        'last_login',
    )

    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password')
        }),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name',)
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'is_administrator',
                'groups', 'user_permissions'),
        }),
        (_('Important dates'), {
            'fields': (
                'last_login', 'date_joined'),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'first_name', 'last_name',
                'is_active', 'is_staff', 'is_superuser'),
        }),
    )


class AuthorizationAdmin(admin.ModelAdmin):

    list_display = (
        'user', 'full_name', 'project', 'level'
    )
    ordering = ('project', 'user__last_name')
    list_editable = ('level', )
    search_fields = ('user__username', )

    def full_name(self, obj):
        return " ".join([obj.user.last_name, obj.user.first_name])


admin.site.register(User, UserAdmin)
admin.site.register(Authorization, AuthorizationAdmin)
admin.site.register(Subscription)
# admin.site.register(UserLevelPermission)
