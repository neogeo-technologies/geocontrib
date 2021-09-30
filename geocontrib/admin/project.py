import logging

from django.contrib.auth import get_user_model
from django.contrib.gis import admin

from geocontrib.forms import ProjectAdminForm
from geocontrib.models import Project
from geocontrib.models import BaseMap
from geocontrib.models import ContextLayer
from geocontrib.models import Layer
from geocontrib.models import Event


logger = logging.getLogger(__name__)
User = get_user_model()


class ContextLayerTabular(admin.TabularInline):
    model = ContextLayer
    extra = 0
    can_delete = True
    can_order = True
    show_change_link = True
    view_on_site = False
    fields = ('order', 'opacity', 'layer', 'queryable')


class BaseMapAdmin(admin.ModelAdmin):

    inlines = (
        ContextLayerTabular,
    )

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)
        ctx_lyrs = ContextLayer.objects.filter(
            base_map=formset.instance).order_by('order')
        for idx, ctx in enumerate(ctx_lyrs):
            ctx.order = idx
            ctx.save(update_fields=['order'])


class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    ordering = ('title', )


admin.site.register(BaseMap, BaseMapAdmin)
admin.site.register(Layer)
admin.site.register(Event)
admin.site.register(Project, ProjectAdmin)
