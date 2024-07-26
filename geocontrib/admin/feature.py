from datetime import date
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.actions import delete_selected
from django.contrib.auth import get_user_model
from django.contrib.gis import admin
from django.contrib.postgres.aggregates import StringAgg
from django.db import connections
from django.db.models import CharField, OuterRef, Subquery, F
from django.forms import formset_factory
from django.forms import modelformset_factory
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import path
from django_admin_listfilter_dropdown.filters import DropdownFilter
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from geocontrib.admin.filters import DeletionOnListFilter
from geocontrib.admin.filters import FeatureTypeFilter
from geocontrib.admin.filters import ProjectFilter
from geocontrib.forms import FeatureTypeAdminForm
from geocontrib.forms import CustomFieldModelAdminForm
from geocontrib.forms import HiddenDeleteBaseFormSet
from geocontrib.forms import HiddenDeleteModelFormSet
from geocontrib.forms import FeatureSelectFieldAdminForm
from geocontrib.forms import AddPosgresViewAdminForm
from geocontrib.models import Attachment
from geocontrib.models import Authorization
from geocontrib.models import Comment
from geocontrib.models import CustomField
from geocontrib.models import Feature
from geocontrib.models import FeatureLink
from geocontrib.models import FeatureType
from geocontrib.models import ImportTask
from geocontrib.models import PreRecordedValues
from geocontrib.tasks import task_geojson_processing


logger = logging.getLogger(__name__)
User = get_user_model()


class CustomFieldAdmin(admin.ModelAdmin):
    list_display = ('label', 'name', 'feature_type', 'project_title')
    ordering = ('feature_type', 'label')

    def project_title(self, obj):
        try:
            title = obj.feature_type.project.title
        except AttributeError:
            title = 'N/A'
        return title


class CustomFieldTabular(admin.TabularInline):
    model = CustomField
    extra = 0
    can_delete = False
    can_order = True
    show_change_link = True
    view_on_site = False


class FeatureTypeAdmin(admin.ModelAdmin):
    """
    Admin interface for managing `FeatureType` models with custom functionality for PostgreSQL view creation.

    This admin class provides:
    - A custom form (`FeatureTypeAdminForm`) for managing `FeatureType` instances.
    - Inline editing of associated `CustomField` models through `CustomFieldTabular`.
    - A custom change form template that includes options for creating PostgreSQL views.
    - Custom URL routing for creating PostgreSQL views associated with `FeatureType` models.
    - Methods for handling the creation of PostgreSQL views, including form processing, SQL execution, and error handling.
    """
    form = FeatureTypeAdminForm # Custom form for `FeatureType` model management.
    inlines = (
        CustomFieldTabular, # Inline formset for `CustomField` models
    )
    change_form_template = 'admin/geocontrib/with_create_postrgres_view.html' # Path to the custom template for editing `FeatureType` models.

    list_display = ('title', 'project') # Fields displayed in the list view of `FeatureType` models
    ordering = ('project', 'title') # Default ordering for the `FeatureType` list view

    delete_selected.short_description = 'Supprimer les éléments sélectionnés de la base de données' # Description for the bulk delete action

    def get_readonly_fields(self, request, obj=None):
        """
        Returns a list of fields that should be read-only based on the edit status of the object.
        """
        if obj:
            return self.readonly_fields + ('geom_type', )
        return self.readonly_fields

    def get_urls(self):
        """
        Adds a custom URL for PostgreSQL view creation.
        """
        urls = super().get_urls()  # Default admin URLs
        my_urls = [
            path(
                '<int:feature_type_id>/create-postgres-view/',  # Custom view creation URL
                self.admin_site.admin_view(self.create_postgres_view),
                name='create_postgres_view'),
        ]
        return my_urls + urls  # Combine with default URLs

    def pop_deleted_forms(self, cleaned_data):
        """
        Removes forms marked for deletion from the cleaned data.
        """
        return [row for row in cleaned_data if row.get('DELETE') is False]

    def exec_sql(self, request, sql_create_view, view_name):
        """
        Executes SQL to create a PostgreSQL view and handles messaging based on success or failure.
        """
        success = False
        with connections['default'].cursor() as cursor:
            try:
                cursor.execute(sql_create_view)  # Execute SQL command
            except Exception as err:
                logger.exception("PostgreSQL view creation failed: {0}".format(sql_create_view))
                messages.error(request, "La vue PostgreSQL n'a pas pu être créée : {0}".format(err))  # Error message
            else:
                messages.success(request, "La vue PostgreSQL '{0}' est disponible. ".format(view_name))  # Success message
                success = True
        return success

    def create_postgres_view(self, request, feature_type_id, *args, **kwargs):
        """
        Handles the creation of a PostgreSQL view for a specific `FeatureType` through a custom admin form.

        This method processes both GET and POST requests:
        - For GET requests, it initializes and displays the form used to create a PostgreSQL view.
        - For POST requests, it processes the form submission, validates the data, generates SQL for the view, and executes the SQL command.

        Args:
            request (HttpRequest): The HTTP request object containing metadata and data for the request.
            feature_type_id (int): The ID of the `FeatureType` model for which the PostgreSQL view is being created.

        Returns:
            HttpResponse: A redirect to the `FeatureType` change page if view creation is successful,
                        or a rendered template response with the form if validation fails or for GET requests.
        """

        # Define formsets for selecting feature details and custom fields
        FeatureDetailSelectionFormset = formset_factory(
            FeatureSelectFieldAdminForm,  # Form for selecting feature details
            formset=HiddenDeleteBaseFormSet,  # Formset class with support for form deletion
            can_delete=True,
            extra=0  # No extra empty forms
        )
        # Define formset for custom fields
        CustomFieldsFormSet = modelformset_factory(
            CustomField,  # Model for custom fields
            can_delete=True,
            form=CustomFieldModelAdminForm,  # Form for editing custom fields
            formset=HiddenDeleteModelFormSet,  # Formset class with support for form deletion
            extra=0  # No extra empty forms
        )

        # Prepare initial data for the feature detail formset
        feature_detail_initial = [{
            'related_field': (
                str(field.name), "{0} - {1}".format(
                    field.name, field.get_internal_type())),
            'alias': None
        } for field in Feature._meta.get_fields() if field.name in ('feature_id', 'title', 'description', 'geom')]

        if request.method == 'POST':
            # Process the form submission
            fds_formset = FeatureDetailSelectionFormset(
                request.POST or None, prefix='fds',
                initial=feature_detail_initial)
            cfs_formset = CustomFieldsFormSet(request.POST or None, prefix='cfs')
            pg_form = AddPosgresViewAdminForm(request.POST or None)

            # Validate all forms
            if fds_formset.is_valid() and pg_form.is_valid() and cfs_formset.is_valid():
                view_name = pg_form.cleaned_data.get('name')  # Get view name from form
                status = pg_form.cleaned_data.get('status') or (stat[0] for stat in Feature.STATUS_CHOICES)  # Get status from form
                fds_data = self.pop_deleted_forms(fds_formset.cleaned_data)  # Filter out deleted feature details
                cfs_data = self.pop_deleted_forms(cfs_formset.cleaned_data)  # Filter out deleted custom fields

                # Generate SQL script for creating the PostgreSQL view
                sql = render_to_string(
                    'sql/create_view.sql',
                    context=dict(
                        fds_data=fds_data,
                        cfs_data=cfs_data,
                        feature_type_id=feature_type_id,
                        status=status,
                        schema=getattr(settings, 'DB_SCHEMA', 'public'),  # Get database schema from settings
                        view_name=view_name,
                        user=settings.DATABASES['default']['USER'],  # Database user from settings
                    ))
                logger.debug(sql)  # Log the generated SQL for debugging

                # Execute the SQL script
                its_alright = self.exec_sql(request, sql, view_name)
                if its_alright:
                    # Redirect to the change page for the FeatureType if view creation is successful
                    return redirect('admin:geocontrib_featuretype_change', feature_type_id)
            else:
                # Log errors if any of the forms are invalid
                for formset in [fds_formset, pg_form, cfs_formset]:
                    logger.error(formset.errors)

        else:
            # Initialize forms for GET request
            pg_form = AddPosgresViewAdminForm()  # Create an empty form for PostgreSQL view details
            fds_formset = FeatureDetailSelectionFormset(
                prefix='fds',
                initial=feature_detail_initial)  # Provide initial data for feature details
            cfs_formset = CustomFieldsFormSet(
                queryset=CustomField.objects.filter(feature_type__pk=feature_type_id),  # Queryset for custom fields related to the feature type
                prefix='cfs')

        # Prepare the context for rendering the template
        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['fds_formset'] = fds_formset
        context['cfs_formset'] = cfs_formset
        context['pg_form'] = pg_form

        # Render the template with the form for creating the PostgreSQL view
        return TemplateResponse(request, "admin/geocontrib/create_postrges_view_form.html", context)


def to_draft(modeladmin, request, queryset):
    for e in queryset:
        e.change_status('draft')
to_draft.short_description = "Changer status à Brouillon"

def to_pending(modeladmin, request, queryset):
    for e in queryset:
        e.change_status('pending')
to_pending.short_description = "Changer status à 'En attente de publication'"

def to_published(modeladmin, request, queryset):
    for e in queryset:
        e.change_status('published')
to_published.short_description = "Changer status à Publié"

def to_archived(modeladmin, request, queryset):
    for e in queryset:
        e.change_status('archived')
to_archived.short_description = "Changer status à Archivé"


class FeatureAdmin(admin.ModelAdmin):
    # Specifies a custom template to use for the 'change' (edit) form in the admin.
    change_form_template = 'admin/geocontrib/feature_no_geom_feat_type_list.html'

    list_display = (
        'title',
        'project',
        'feature_type_title',
        'status',
        'contributeurs',
        'deletion_on'
    )
    list_filter = (
        ('project__slug', DropdownFilter),
        ('feature_type__title', DropdownFilter),
        'status',
        ('creator', RelatedDropdownFilter),
        (DeletionOnListFilter),
    )
    actions = (
        'to_draft',
        'to_pending',
        'to_published',
        'to_archived',
        'to_erased'
    )
    ordering = ('project', 'feature_type', 'title')

    def contributeur(self, obj):
        contributeurs = Authorization.objects.filter(
            level__rank=2, project=obj.feature_type.project.pk
            ).values_list('user__username', flat=True)
        list_contributeurs = [contributeur for contributeur in contributeurs]
        return list_contributeurs
    contributeur.short_description = 'Contributeur'

    def get_feature_type(self, obj):
        res = "N/A"
        try:
            res = obj.feature_type.title
        except Exception:
            pass
        return res
    get_feature_type.short_description = 'Type de signalement'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        contributeurs = Authorization.objects.filter(
            project=OuterRef('project'), level__rank=2
        ).values('project').annotate(
            usernames=StringAgg('user__username', ', ')
        ).values('usernames')

        return queryset.annotate(
            contributeurs=Subquery(contributeurs, output_field=CharField()),
            feature_type_title=F('feature_type__title')
        )

    def feature_type_title(self, obj):
        return obj.feature_type_title
    feature_type_title.short_description = "Type de signalement"
    feature_type_title.admin_order_field = 'feature_type__title'

    def contributeurs(self, obj):
        return obj.contributeurs
    contributeurs.short_description = "Contributeurs"
    contributeurs.admin_order_field = 'creator__username'

    def to_draft(self, request, queryset):
        queryset.update(status='draft')
    to_draft.short_description = "Changer status à Brouillon"

    def to_pending(self, request, queryset):
        queryset.update(status='pending')
    to_pending.short_description = "Changer status à 'En attente de publication'"

    def to_published(self, request, queryset):
        queryset.update(status='published')
    to_published.short_description = "Changer status à Publié"

    def to_archived(self, request, queryset):
        queryset.update(status='archived')
    to_archived.short_description = "Changer status à Archivé"

    def to_erased(self, request, queryset):
        queryset.update(deletion_on=date.today())
    to_erased.short_description = "Supprimer les signalements sélectionnés"

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Overridden change_view method to add custom context to the admin change form.

        Args:
            request: HttpRequest object representing current request.
            object_id: ID of the object being changed.
            form_url: URL for the form endpoint.
            extra_context: Dictionary containing context data (default is None).

        Returns:
            HttpResponse object representing the rendered change form.
        """
        # Ensure extra_context is a dictionary.
        extra_context = extra_context or {}

        # Query FeatureType instances where geom_type is 'none'.
        no_geom_feat_types = FeatureType.objects.filter(geom_type='none')

        # Extract the titles of these instances into a list.
        no_geom_feat_type_titles = [feat_type.title for feat_type in no_geom_feat_types]

        # Add this list to the context under the key 'no_geom_feat_type_list'.
        extra_context['no_geom_feat_type_list'] = no_geom_feat_type_titles

        # Call the superclass method and return its result.
        return super().change_view(request, object_id, form_url, extra_context)


class FeatureLinkAdmin(admin.ModelAdmin):
    list_filter = (
        ProjectFilter,
        FeatureTypeFilter,
        'relation_type',
    )

    search_fields = (
        'feature_from__title',
        'feature_to__title'
    )

    list_display = (
        'feature_from',
        'get_status',
        'get_creator_from',
        'get_created_on',
        'relation_type',
        '_feature_to',
        'get_feature_type',
    )

    list_per_page = 10

    def get_queryset(self, request):
        user = request.user
        qs = super().get_queryset(request)
        if user.is_superuser:
            return qs
        moderation_projects_pk = Authorization.objects.filter(
            user=user, level__rank__gte=3
        ).values_list('project__pk', flat=True)
        return qs.filter(feature_to__project__in=moderation_projects_pk)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('relation_type', 'feature_from', 'feature_to')
        return self.readonly_fields

    def get_creator_from(self, obj):
        res = "N/A"
        try:
            res = obj.feature_from.display_creator
        except Exception:
            pass
        return res
    get_creator_from.admin_order_field = 'feature_from__creator__last_name'
    get_creator_from.short_description = 'Créateur (source)'

    def get_created_on(self, obj):
        res = "N/A"
        try:
            res = obj.feature_from.created_on.strftime("%d/%m/%Y %H:%M")
        except Exception:
            pass
        return res
    get_created_on.admin_order_field = 'feature_from__created_on'
    get_created_on.short_description = 'Date création (source)'

    def get_status(self, obj):
        res = "N/A"
        try:
            res = obj.feature_from.get_status_display()
        except Exception:
            pass
        return res
    get_status.short_description = 'Statut (source)'

    def get_feature_type(self, obj):
        res = "N/A"
        try:
            res = obj.feature_from.feature_type.title
        except Exception:
            pass
        return res
    get_feature_type.short_description = 'Type de signalement'

    def _feature_to(self, obj):
        res = "N/A"
        try:
            feat = obj.feature_to
            res = "{0} ({1}, {2}) - {3}".format(
                feat.title, feat.display_creator,
                feat.created_on.strftime("%d/%m/%Y %H:%M"),
                feat.get_status_display())
        except Exception:
            pass
        return res
    _feature_to.short_description = 'Signalement (lié)'

    actions = [
        'set_replacing',
        'set_replaced_by',
        'set_depends_on',
        'delete_instances',
        'delete_feature_from',
    ]

    def delete_instances(self, request, queryset):
        for elm in queryset:
            elm.delete()
    delete_instances.short_description = "Effacer ces liaisons entre signalements"

    def delete_feature_from(self, request, queryset):
        for elm in queryset:
            # Supprime de fait la feature_link et son inverse
            elm.feature_from.delete()
    delete_feature_from.short_description = "Supprimer ces signalements"

    def set_replacing(self, request, queryset):
        for elm in queryset:
            elm.update_relations('remplace')
    set_replacing.short_description = "Mettre 'Remplace' dans la liaison de ce signalement"

    def set_replaced_by(self, request, queryset):
        for elm in queryset:
            elm.update_relations('est_remplace_par')
    set_replaced_by.short_description = "Mettre 'Est remplacer par' dans la liaison de ce signalement"

    def set_depends_on(self, request, queryset):
        for elm in queryset:
            elm.update_relations('depend_de')
    set_depends_on.short_description = "Mettre 'Dépend de' dans la liaison de ce signalement"

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            # Remplacer par delete_instances() qui
            del actions['delete_selected']
        return actions


class ImportTaskAdmin(admin.ModelAdmin):

    actions = (
        'import_geojson',
    )

    def import_geojson(self, request, queryset):
        for import_task in queryset:
            task_geojson_processing.apply_async(kwargs={'import_task_id': import_task.pk})
        messages.info(request, 'Le traitement des données est en cours.')
    import_geojson.short_description = "Appliquer les opérations d'import"


class AttachmentAdmin(admin.ModelAdmin):
    list_display=('title', 'project')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('feature_type_slug', 'created_on', 'comment', 'project',)
    ordering = ('feature_type_slug', 'created_on', 'comment', 'project',)


admin.site.register(CustomField, CustomFieldAdmin)
admin.site.register(Feature, FeatureAdmin)
admin.site.register(FeatureType, FeatureTypeAdmin)
admin.site.register(FeatureLink, FeatureLinkAdmin)
admin.site.register(ImportTask, ImportTaskAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(PreRecordedValues)
