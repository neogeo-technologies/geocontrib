from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib import admin
from django.apps import apps
from collab.models import Autorisation
from collab.models import CustomUser
from collab.models import Project
# from collab.models import Status
from collab.models import Subscription

app = apps.get_app_config('collab')

# class StatusAdmin(admin.ModelAdmin):
#     # readonly_fields = ('status',)
#     list_display = ('status', )
#     empty_value_display = '-aucun-'
# admin.site.register(Status, StatusAdmin)

class ProjectAdmin(admin.ModelAdmin):
    readonly_fields = ('slug', 'feature_type')
    list_display = ('title', 'thumbLink', 'moderation')
    empty_value_display = '-aucun-'
admin.site.register(Project, ProjectAdmin)


class AutorisationAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'level')
    empty_value_display = '-aucun-'
admin.site.register(Autorisation, AutorisationAdmin)

# class SubscriptionAdmin(admin.ModelAdmin):
#     list_display = ('user', 'feature_id')
#     readonly_fields = ('slug',)
#     empty_value_display = '-aucun-'
# admin.site.register(Subscription, SubscriptionAdmin)


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('nickname',)}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filters = ('is_active',)
admin.site.register(CustomUser, CustomUserAdmin)


for model_name, model in app.models.items():

    if 'auth' not in model_name and 'django' not in model_name and 'customuser_' not in model_name:
        if not admin.site._registry.get(model, ''):
            # import pdb; pdb.set_trace()

            if 'feature' in model_name:
                model_admin = type(model_name + "Admin", (admin.ModelAdmin, ), {'list_display': tuple([field.name for field in model._meta.fields]),  'readonly_fields':('feature_id',)})
                admin.site.register(model, model_admin)
            else:
                admin.site.register(model)
