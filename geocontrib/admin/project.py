import logging

from django.contrib.auth import get_user_model
from django.contrib.gis import admin
from django.http import JsonResponse


from geocontrib.forms import ProjectAdminForm
from geocontrib.forms import ProjectAttributeAdminForm
from geocontrib.models import Project
from geocontrib.models import ProjectAttribute
from geocontrib.models import ProjectAttributeAssociation
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
    """
    Defines an inline administration interface for ProjectAttributeAssociation.
    This allows editing of ProjectAttributeAssociations directly within the Project admin page.
    """
    model = ProjectAttributeAssociation
    fk_name = "project"  # Specifies the ForeignKey field to the parent Project model.
    extra = 0  # Specifies the number of extra blank forms to be displayed. Setting it to 0 to avoid having to manage its customization

    class Media:
        """
        Includes custom JavaScript in the admin page for this inline.
        This JavaScript can be used to add dynamic behaviors to the inline forms.
        """
        js = ('admin/js/project_attribute_association.js',)

class ProjectAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Project model.
    """
    form = ProjectAdminForm  # Specifies the custom form to use for editing Projects.
    ordering = ('title',)  # Orders Projects by their title in the admin listing.
    inlines = [ProjectAttributeAssociationInline]  # Includes ProjectAttributeAssociationInline within the Project admin.
    change_form_template = 'admin/geocontrib/project_attribute_data_container.html'  # Custom template for the change form.

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """
        Overrides the change form view to pass additional context to the template.
        This is used to inject 'attributes_data', containing all ProjectAttributes,
        as a JSON string into the page for use by custom JavaScript.
        """
        extra_context = extra_context or {}
        attributes = ProjectAttribute.objects.all()
        extra_context['attributes_data'] = JsonResponse(list(attributes.values('id', 'name', 'field_type', 'options')), safe=False).content.decode('utf-8')
        return super().changeform_view(request, object_id, form_url, extra_context)

class ProjectAttributeAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ProjectAttribute model.
    """
    form = ProjectAttributeAdminForm  # Specifies the custom form for editing ProjectAttributes.
    fields = ['label', 'name', 'field_type', 'options', 'default_value', 'display_filter', 'default_filter_enabled', 'default_filter_value'] # Explicitly lists all fields to include in the form.

    def get_readonly_fields(self, request, obj=None):
        """
        Dynamically determines which fields should be readonly in the admin form.
        If editing an existing instance (obj is not None), all fields except 'label' and 'name'
        are set to readonly. If creating a new instance (obj is None), no fields are set to readonly.
        """
        if obj:  # Editing an existing instance
            return [f.name for f in self.model._meta.fields if f.name not in ('label', 'name', 'options', 'default_value', 'display_filter', 'default_filter_enabled', 'default_filter_value')]
        return []  # Creating a new instance

    class Media:
        """
        Includes custom JavaScript for the ProjectAttribute admin page.
        This JavaScript can be used for dynamic form behaviors specific to ProjectAttribute.
        """
        js = ('admin/js/project_attribute.js',)

admin.site.register(BaseMap, BaseMapAdmin)
admin.site.register(Layer)
admin.site.register(Event)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectAttribute, ProjectAttributeAdmin)
