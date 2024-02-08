import logging

from django.contrib.auth import get_user_model
from django.contrib.gis import admin
from django.http import JsonResponse


from geocontrib.forms import ProjectAdminForm
from geocontrib.forms import ProjectAttributeAdminForm
from geocontrib.models import Project, ProjectAttribute, ProjectAttributeAssociation
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

class ProjectAttributeAssociationInline(admin.TabularInline):
    model = ProjectAttributeAssociation
    fk_name = "project"
    extra = 1  # Nombre de formulaires vides à afficher

    class Media:
        js = ('admin/js/project_attribute_association.js',) 

class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    ordering = ('title', )
    inlines = [ProjectAttributeAssociationInline]
    change_form_template = 'admin/geocontrib/project_attribute_data_container.html'

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        attributes = ProjectAttribute.objects.all()
        extra_context['attributes_data'] = JsonResponse(list(attributes.values('id', 'name', 'field_type', 'options')), safe=False).content.decode('utf-8')
        return super().changeform_view(request, object_id, form_url, extra_context)

class ProjectAttributeAdmin(admin.ModelAdmin):
    form = ProjectAttributeAdminForm

    class Media:
        js = ('admin/js/project_attribute.js',)

admin.site.register(BaseMap, BaseMapAdmin)
admin.site.register(Layer)
admin.site.register(Event)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectAttribute, ProjectAttributeAdmin)
