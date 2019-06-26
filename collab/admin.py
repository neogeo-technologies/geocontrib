from collab.actions import delete_project
from django.contrib.admin import site
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib import admin
from django.apps import apps
from collab.models import Attachment
from collab.models import Autorisation
from collab.models import CustomUser
from collab.models import Comment
from collab.models import Event
from collab.models import FeatureType
from collab.models import Project
# from collab.models import Status
from collab.models import Subscription

app = apps.get_app_config('collab')


class CommentAdmin(admin.ModelAdmin):
    readonly_fields = ('feature_type_slug',)
    list_display = ('project', 'author', 'creation_date')
    empty_value_display = '-aucun-'
admin.site.register(Comment, CommentAdmin)


class AttachmentAdmin(admin.ModelAdmin):
    readonly_fields = ('feature_id', 'comment')
    list_display = ('title', 'project', 'author')
    empty_value_display = '-aucun-'
admin.site.register(Attachment, AttachmentAdmin)




class ProjectAdmin(admin.ModelAdmin):
    readonly_fields = ('slug',)
    list_display = ('title', 'thumbLink', 'moderation')
    empty_value_display = '-aucun-'
    actions = [delete_project]
    # supprimer l'action de base de suppression d'un projet
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
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

# class ProjectInline(admin.TabularInline):
#     fields = ['title', 'slug']
#     readonly_fields = ['title', 'slug']
#     model = Project

class FeatureTypeAdmin(admin.ModelAdmin):
    # inlines = [
    #     ProjectInline,
    # ]
    readonly_fields = ('name', 'feature_type_slug', 'geom_type',
                       'user', 'wording')
    list_display = ('name', 'feature_type_slug', 'project', 'geom_type',)
    empty_value_display = '-aucun-'
admin.site.register(FeatureType, FeatureTypeAdmin)


class EventAdmin(admin.ModelAdmin):

    readonly_fields = ('project_slug', 'feature_type_slug', 'feature_id',
                       'comment_id', 'attachment_id')
    list_display = ('project_slug', 'event_type', 'creation_date',)
    empty_value_display = '-aucun-'
admin.site.register(Event, EventAdmin)


class SubscriptionAdmin(admin.ModelAdmin):

    readonly_fields = ('creation_date', 'feature_id',
                       'project_slug', 'users', 'feature_type_slug')
    list_display = ('creation_date', 'feature_id', 'project_slug')
    empty_value_display = '-aucun-'
admin.site.register(Subscription, SubscriptionAdmin)


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


# for model_name, model in app.models.items():
#     if 'auth' not in model_name and 'django' not in model_name and 'customuser_' not in model_name:
#         if not admin.site._registry.get(model, ''):
#             admin.site.register(model)
