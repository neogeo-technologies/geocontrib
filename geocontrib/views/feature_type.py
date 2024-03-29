from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos.error import GEOSException
from django.forms import modelformset_factory
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.detail import SingleObjectMixin

from geocontrib import logger
from geocontrib.exif import exif
from api.serializers import FeatureTypeSerializer
from geocontrib.forms import CustomFieldModelBaseFS
from geocontrib.forms import CustomFieldModelForm
from geocontrib.forms import FeatureTypeModelForm
from geocontrib.models import Authorization
from geocontrib.models import CustomField
from geocontrib.models import Feature
from geocontrib.models import FeatureType
from geocontrib.models import ImportTask
from geocontrib.models import Project
from geocontrib.views.common import DECORATORS
from geocontrib.tasks import task_geojson_processing, task_csv_processing


@method_decorator(DECORATORS, name='dispatch')
class FeatureTypeCreate(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = Project.objects.all()
    CustomFieldsFormSet = modelformset_factory(
        CustomField,
        can_delete=True,
        form=CustomFieldModelForm,
        formset=CustomFieldModelBaseFS,
        extra=0,
    )

    def test_func(self):
        user = self.request.user
        project = self.get_object()
        return Authorization.has_permission(user, 'can_create_feature_type', project)

    def get(self, request, slug):
        project = self.get_object()
        user = request.user
        slug = request.GET.get('create_from')
        feature_type = FeatureType.objects.filter(slug=slug).first()
        if feature_type and isinstance(feature_type, FeatureType):
            initial = model_to_dict(feature_type)
            if initial.get('title'):
                initial.update({
                    'title': "{} (Copie {})".format(
                        initial['title'],
                        timezone.now().strftime("%d/%m/%Y %H:%M"))
                })
            form = FeatureTypeModelForm(initial=initial)
            formset = self.CustomFieldsFormSet(
                queryset=CustomField.objects.filter(feature_type=feature_type),
            )
        else:
            form = FeatureTypeModelForm()
            formset = self.CustomFieldsFormSet(queryset=CustomField.objects.none())

        context = {
            'form': form,
            'formset': formset,
            'permissions': Authorization.all_permissions(user, project),
            'feature_types': project.featuretype_set.all(),
            'project': project,
            'title': "Création d'un type de signalement",
        }
        return render(request, 'geocontrib/feature_type/feature_type_create.html', context)

    def post(self, request, slug):
        user = request.user
        form = FeatureTypeModelForm(request.POST or None)
        project = self.get_object()
        formset = self.CustomFieldsFormSet(request.POST or None)
        if form.is_valid() and formset.is_valid():
            feature_type = form.save(commit=False)
            feature_type.project = project
            feature_type.save()

            for data in formset.cleaned_data:
                if not data.get("DELETE"):
                    CustomField.objects.create(
                        feature_type=feature_type,
                        position=data.get("position"),
                        label=data.get("label"),
                        name=data.get("name"),
                        field_type=data.get("field_type"),
                        options=data.get("options"),
                    )
            return redirect('geocontrib:project', slug=project.slug)
        else:
            context = {
                'form': form,
                'formset': formset,
                'permissions': Authorization.all_permissions(user, project),
                'feature_types': project.featuretype_set.all(),
                'project': project,
                'title': "Création d'un type de signalement",
            }
            return render(request, 'geocontrib/feature_type/feature_type_create.html', context)


@method_decorator(DECORATORS[0], name='dispatch')
class FeatureTypeDetail(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = FeatureType.objects.all()
    slug_url_kwarg = 'feature_type_slug'

    def test_func(self):
        user = self.request.user
        feature_type = self.get_object()
        project = feature_type.project
        return Authorization.has_permission(user, 'can_view_feature_type', project)

    def get(self, request, slug, feature_type_slug):
        feature_type = self.get_object()
        project = feature_type.project
        user = request.user
        features = Feature.handy.availables(
            user, project
        ).filter(
            feature_type=feature_type
        ).order_by('-updated_on')[:5]

        structure = FeatureTypeSerializer(feature_type, context={'request': request})

        context = {
            'feature_type': feature_type,
            'permissions': Authorization.all_permissions(user, project),
            'feature_types': project.featuretype_set.all(),
            'features': features,
            'project': project,
            'structure': structure.data,
            'title': feature_type.title,
        }

        return render(request, 'geocontrib/feature_type/feature_type_detail.html', context)


@method_decorator(DECORATORS, name='dispatch')
class FeatureTypeUpdate(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = FeatureType.objects.all()
    slug_url_kwarg = 'feature_type_slug'
    CustomFieldsFormSet = modelformset_factory(
        CustomField,
        can_delete=True,
        form=CustomFieldModelForm,
        formset=CustomFieldModelBaseFS,
        extra=0,
    )

    def test_func(self):
        user = self.request.user
        feature_type = self.get_object()
        project = feature_type.project
        # On interdit l'édition d'un feature_type si des signalements ont déja été crée
        if Feature.objects.filter(feature_type=feature_type).exists():
            return False
        return Authorization.has_permission(user, 'can_create_feature_type', project)

    def get(self, request, slug, feature_type_slug):

        feature_type = self.get_object()
        form = FeatureTypeModelForm(instance=feature_type)
        formset = self.CustomFieldsFormSet(
            queryset=CustomField.objects.filter(feature_type=feature_type)
        )
        project = feature_type.project
        user = request.user
        features = Feature.handy.availables(
            user, project
        ).filter(
            feature_type=feature_type
        ).order_by('-updated_on')[:5]

        structure = FeatureTypeSerializer(feature_type, context={'request': request})

        context = {
            'feature_type': feature_type,
            'permissions': Authorization.all_permissions(user, project),
            'features': features,
            'project': project,
            'structure': structure.data,
            'form': form,
            'formset': formset,
            'title': feature_type.title,
        }

        return render(request, 'geocontrib/feature_type/feature_type_edit.html', context)

    def post(self, request, slug, feature_type_slug):
        user = request.user
        feature_type = self.get_object()
        form = FeatureTypeModelForm(request.POST or None, instance=feature_type)
        formset = self.CustomFieldsFormSet(data=request.POST or None)
        if form.is_valid() and formset.is_valid():

            updated_feature_type = form.save()

            for data in formset.cleaned_data:
                custom_field = data.pop('id', None)

                if custom_field and data.get('DELETE'):
                    custom_field.delete()

                if custom_field and not data.get('DELETE'):
                    for key in ['name', 'field_type', 'position', 'label', 'options']:
                        setattr(custom_field, key, data.get(key))
                    custom_field.save()

                if not custom_field and not data.get('DELETE'):
                    CustomField.objects.create(
                        name=data.get('name'),
                        field_type=data.get('field_type'),
                        position=data.get('position'),
                        label=data.get('label'),
                        options=data.get('options'),
                        feature_type=updated_feature_type,
                    )
            return redirect('geocontrib:project', slug=feature_type.project.slug)
        else:

            logger.error(form.errors)
            logger.error(formset.errors)
            messages.error(
                request,
                "Erreur lors de l'édition du type de signalement. ")
            context = {
                'form': form,
                'formset': formset,
                'permissions': Authorization.all_permissions(user, feature_type.project),
                'project': feature_type.project,
                'feature_type': feature_type,
                'title': feature_type.title
            }
        return render(request, 'geocontrib/feature_type/feature_type_edit.html', context)


@method_decorator(DECORATORS, name='dispatch')
class ImportFromGeoJSON(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = FeatureType.objects.all()
    slug_url_kwarg = 'feature_type_slug'

    def test_func(self):
        user = self.request.user
        feature_type = self.get_object()
        project = feature_type.project
        return Authorization.has_permission(user, 'can_create_feature', project)

    def post(self, request, slug, feature_type_slug):
        feature_type = self.get_object()
        try:
            up_file = request.FILES['json_file']
            import_task = ImportTask.objects.create(
                created_on=timezone.now(),
                project=feature_type.project,
                feature_type=feature_type,
                user=request.user,
                geojson_file=up_file
            )
        except Exception:
            messages.error(request, "Erreur à l'import du fichier. ")
        else:
            task_geojson_processing.apply_async(kwargs={'import_task_id': import_task.pk})
            messages.info(request, "L'import du fichier réussi. Le traitement des données est en cours. ")
        return redirect('geocontrib:feature_type_detail', slug=slug, feature_type_slug=feature_type_slug)


@method_decorator(DECORATORS, name='dispatch')
class ImportFromCSV(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = FeatureType.objects.all()
    slug_url_kwarg = 'feature_type_slug'

    def test_func(self):
        user = self.request.user
        feature_type = self.get_object()
        project = feature_type.project
        return Authorization.has_permission(user, 'can_create_feature', project)

    def post(self, request, slug, feature_type_slug):
        feature_type = self.get_object()
        try:
            up_file = request.FILES['csv_file']
            import_task = ImportTask.objects.create(
                created_on=timezone.now(),
                project=feature_type.project,
                feature_type=feature_type,
                user=request.user,
                geojson_file=up_file
            )
        except Exception:
            messages.error(request, "Erreur à l'import du fichier. ")
        else:
            task_csv_processing.apply_async(kwargs={'import_task_id': import_task.pk})
            messages.info(request, "L'import du fichier réussi. Le traitement des données est en cours. ")
        return redirect('geocontrib:feature_type_detail', slug=slug, feature_type_slug=feature_type_slug)


@method_decorator(DECORATORS, name='dispatch')
class ImportFromImage(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = FeatureType.objects.all()
    slug_url_kwarg = 'feature_type_slug'

    def test_func(self):
        user = self.request.user
        feature_type = self.get_object()
        project = feature_type.project
        return Authorization.has_permission(user, 'can_create_feature', project)

    def get_geom(self, geom):

        # Si geoJSON
        if isinstance(geom, dict):
            geom = str(geom)
        try:
            geom = GEOSGeometry(geom, srid=4326)
        except (GEOSException, ValueError):
            geom = None
        return geom

    def post(self, request, slug, feature_type_slug):

        context = {}
        try:
            up_file = request.FILES['image_file']
        except Exception:
            logger.exception('ImportFromImage.post')
            context['status'] = "error"
            context['message'] = "Erreur à l'import du fichier. "
            status = 400

        try:
            data_geom_wkt = exif.get_image_geoloc_as_wkt(up_file, with_alt=False, ewkt=False)
        except Exception:
            logger.exception('ImportFromImage.post')
            context['status'] = "error"
            context['message'] = "Erreur lors de la lecture des données GPS. "
            status = 400
        else:
            geom = self.get_geom(data_geom_wkt)
            context['geom'] = geom.wkt
            context['status'] = "success"
            status = 200

        return JsonResponse(context, status=status)
