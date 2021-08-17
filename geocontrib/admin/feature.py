import logging

from django.conf import settings
from django.contrib import messages
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

from geocontrib.admin.filters import FeatureTypeFilter
from geocontrib.admin.filters import ProjectFilter
from geocontrib.forms import FeatureTypeAdminForm
from geocontrib.forms import CustomFieldModelAdminForm
from geocontrib.forms import HiddenDeleteBaseFormSet
from geocontrib.forms import HiddenDeleteModelFormSet
from geocontrib.forms import FeatureSelectFieldAdminForm
from geocontrib.forms import AddPosgresViewAdminForm
from geocontrib.models import Authorization
from geocontrib.models import Feature
from geocontrib.models import FeatureType
from geocontrib.models import FeatureLink
from geocontrib.models import CustomField
from geocontrib.models import ImportTask
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
    form = FeatureTypeAdminForm
    inlines = (
        CustomFieldTabular,
    )
    change_form_template = 'admin/geocontrib/with_create_postrgres_view.html'

    list_display = ('title', 'project')

    ordering = ('project', 'title')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('geom_type', )
        return self.readonly_fields

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                '<int:feature_type_id>/create-postgres-view/',
                self.admin_site.admin_view(self.create_postgres_view),
                name='create_postgres_view'),
        ]
        return my_urls + urls

    def pop_deleted_forms(self, cleaned_data):
        return [row for row in cleaned_data if row.get('DELETE') is False]

    def exec_sql(self, request, sql_create_view, view_name):
        success = False
        with connections['default'].cursor() as cursor:
            try:
                cursor.execute(sql_create_view)
            except Exception as err:
                logger.exception("PostgreSQL view creation failed: {0}".format(sql_create_view))
                messages.error(request, "La vue PostgreSQL n'a pas pu être créée : {0}".format(err))
            else:
                messages.success(request, "La vue PostgreSQL '{0}' est disponible. ".format(view_name))
                success = True
        return success

    def create_postgres_view(self, request, feature_type_id, *args, **kwargs):

        FeatureDetailSelectionFormset = formset_factory(
            FeatureSelectFieldAdminForm,
            formset=HiddenDeleteBaseFormSet,
            can_delete=True,
            extra=0
        )

        CustomFieldsFormSet = modelformset_factory(
            CustomField,
            can_delete=True,
            form=CustomFieldModelAdminForm,
            formset=HiddenDeleteModelFormSet,
            extra=0,
        )

        feature_detail_initial = [{
            'related_field': (
                str(field.name), "{0} - {1}".format(
                    field.name, field.get_internal_type())),
            'alias': None
        } for field in Feature._meta.get_fields() if field.name in ('feature_id', 'title', 'description', 'geom')]

        if request.method == 'POST':
            fds_formset = FeatureDetailSelectionFormset(
                request.POST or None, prefix='fds',
                initial=feature_detail_initial)
            cfs_formset = CustomFieldsFormSet(request.POST or None, prefix='cfs')
            pg_form = AddPosgresViewAdminForm(request.POST or None)
            if fds_formset.is_valid() and pg_form.is_valid() and cfs_formset.is_valid():
                view_name = pg_form.cleaned_data.get('name')
                status = pg_form.cleaned_data.get('status') or (stat[0] for stat in Feature.STATUS_CHOICES)
                fds_data = self.pop_deleted_forms(fds_formset.cleaned_data)
                cfs_data = self.pop_deleted_forms(cfs_formset.cleaned_data)

                sql = render_to_string(
                    'sql/create_view.sql',
                    context=dict(
                        fds_data=fds_data,
                        cfs_data=cfs_data,
                        feature_type_id=feature_type_id,
                        status=status,
                        schema=getattr(settings, 'DB_SCHEMA', 'public'),
                        view_name=view_name,
                        user=settings.DATABASES['default']['USER'],
                    ))
                logger.debug(sql)
                its_alright = self.exec_sql(request, sql, view_name)
                if its_alright:
                    return redirect('admin:geocontrib_featuretype_change', feature_type_id)

            else:
                for formset in [fds_formset, pg_form, cfs_formset]:
                    logger.error(formset.errors)

        else:
            pg_form = AddPosgresViewAdminForm()
            fds_formset = FeatureDetailSelectionFormset(
                prefix='fds',
                initial=feature_detail_initial)
            cfs_formset = CustomFieldsFormSet(
                queryset=CustomField.objects.filter(feature_type__pk=feature_type_id),
                prefix='cfs')

        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['fds_formset'] = fds_formset
        context['cfs_formset'] = cfs_formset
        context['pg_form'] = pg_form

        return TemplateResponse(request, "admin/geocontrib/create_postrges_view_form.html", context)


class FeatureAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'project',
        'feature_type_title',
        'status',
        'contributeurs'
    )
    list_filter = (
        ('project__slug', DropdownFilter),
        ('feature_type__title', DropdownFilter),
        'status',
        ('creator', RelatedDropdownFilter),
    )
    actions = (
        'to_draft',
        'to_pending',
        'to_published',
        'to_archived'
    )
    ordering = (
        'project',
        'title'
    )

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


admin.site.register(CustomField, CustomFieldAdmin)
admin.site.register(Feature, FeatureAdmin)
admin.site.register(FeatureType, FeatureTypeAdmin)
admin.site.register(FeatureLink, FeatureLinkAdmin)
admin.site.register(ImportTask, ImportTaskAdmin)
