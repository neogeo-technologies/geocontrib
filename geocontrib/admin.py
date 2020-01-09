from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.gis import admin
from django.utils.translation import ugettext_lazy as _
from django import forms

from geocontrib.models import Authorization
from geocontrib.models import Feature
from geocontrib.models import Project
from geocontrib.models import Subscription
from geocontrib.models import FeatureType
from geocontrib.models import Layer
from geocontrib.models import CustomField
from geocontrib.models import UserLevelPermission
# from geocontrib.models import CustomFieldInterface

User = get_user_model()


class UserAdmin(DjangoUserAdmin):

    list_display = (
        'email', 'last_name', 'first_name',
        'is_superuser', 'is_administrator', 'is_staff', 'is_active'
    )
    search_fields = ('id', 'email', 'first_name', 'last_name')

    ordering = ('-pk', )
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
                'username', 'email', 'password1', 'password2', 'first_name', 'last_name',
                'is_active', 'is_staff', 'is_superuser'),
        }),
    )


class CustomFieldTabular(admin.TabularInline):
    model = CustomField
    extra = 0
    can_delete = False
    can_order = True
    show_change_link = True
    view_on_site = False


class FeatureTypeForm(forms.ModelForm):
    class Meta:
        model = FeatureType
        fields = '__all__'
        widgets = {
            'color': forms.widgets.TextInput(attrs={'type': 'color'}),
        }


class FeatureTypeAdmin(admin.ModelAdmin):
    form = FeatureTypeForm
    readonly_fields = ('geom_type', )
    inlines = (
        CustomFieldTabular,
    )


admin.site.register(User, UserAdmin)
admin.site.register(CustomField)
admin.site.register(Layer)
admin.site.register(Authorization)
admin.site.register(Feature)
admin.site.register(FeatureType, FeatureTypeAdmin)
admin.site.register(Project)
admin.site.register(Subscription)
admin.site.register(UserLevelPermission)
# admin.site.register(CustomFieldInterface)
