import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.gis import admin
from django.utils.translation import gettext_lazy as _

from geocontrib.models import Authorization
from geocontrib.models import Subscription
from geocontrib.models import UsersGroup
from geocontrib.models import UserGroupMembership


logger = logging.getLogger(__name__)
User = get_user_model()

class UserGroupMembershipInline(admin.TabularInline):  # Utilisation d'un inline
    model = UserGroupMembership
    extra = 0  # Nombre de lignes vides affichées pour ajouter une nouvelle association
    autocomplete_fields = ["group"]  # Permet la sélection rapide du groupe via recherche


class UserAdmin(DjangoUserAdmin):
    # if users added/managed externally, hide button to create user from django admin
    if settings.HIDE_USER_CREATION_BUTTON:
        def has_add_permission(self, request):
            return False
    
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

    inlines = [UserGroupMembershipInline]


class UsersGroupAdmin(admin.ModelAdmin):
    list_display = ('codename', 'display_name', 'usergroup_type', 'is_global')
    search_fields = ('display_name',)

class UserGroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'joined_at')
    search_fields = ('user__username', 'group__display_name')
    list_filter = ('group',)
    ordering = ('group', 'user__username')
    autocomplete_fields = ['user', 'group']


class AuthorizationAdmin(admin.ModelAdmin):

    list_display = (
        'user', 'full_name', 'project', 'level'
    )
    ordering = ('project', 'user__last_name')
    list_editable = ('level', )
    search_fields = ('user__username', )

    def full_name(self, obj):
        return " ".join([obj.user.last_name, obj.user.first_name])
    
class SubscriptionAdmin(admin.ModelAdmin):
    list_display=('project',)

admin.site.register(User, UserAdmin)
admin.site.register(Authorization, AuthorizationAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(UsersGroup, UsersGroupAdmin)
admin.site.register(UserGroupMembership, UserGroupMembershipAdmin)

# admin.site.register(UserLevelPermission)
