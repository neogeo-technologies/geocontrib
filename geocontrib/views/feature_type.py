import json

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos.error import GEOSException
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.forms import modelformset_factory
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.detail import SingleObjectMixin

from api.serializers import FeatureTypeSerializer
from geocontrib import logger
from geocontrib.exif import exif
from geocontrib.forms import CustomFieldModelBaseFS
from geocontrib.forms import CustomFieldModelForm
from geocontrib.forms import FeatureTypeModelForm
from geocontrib.models import Authorization
from geocontrib.models import CustomField
from geocontrib.models import Feature
from geocontrib.models import FeatureLink
from geocontrib.models import FeatureType
from geocontrib.models import Project
from geocontrib.views.common import DECORATORS


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

    def get_geom(self, geom):

        # Si geoJSON
        if isinstance(geom, dict):
            geom = str(geom)
        try:
            geom = GEOSGeometry(geom, srid=4326)
        except (GEOSException, ValueError):
            geom = None
        return geom

    def get_feature_data(self, feature_type, properties, field_names):

        feature_data = {}
        if hasattr(feature_type, 'customfield_set'):
            for field in field_names:
                feature_data[field] = properties.get(field)
        return feature_data

    def create_features(self, request, creator, data, feature_type):
        new_features = data.get('features')
        nb_features = len(new_features)
        field_names = feature_type.customfield_set.values_list('name', flat=True)

        for feature in new_features:
            properties = feature.get('properties')
            feature_data = self.get_feature_data(feature_type, properties, field_names)
            title = properties.get('title')
            description = properties.get('description')
            current = Feature.objects.create(
                title=title,
                description=description,
                status='draft',
                creator=creator,
                project=feature_type.project,
                feature_type=feature_type,
                geom=self.get_geom(feature.get('geometry')),
                feature_data=feature_data,
            )
            if title:
                simili_features = Feature.objects.filter(
                    Q(title=title, description=description, feature_type=feature_type) | Q(geom=current.geom)
                ).exclude(feature_id=current.feature_id)

                if simili_features.count() > 0:
                    for row in simili_features:
                        FeatureLink.objects.get_or_create(
                            relation_type='doublon',
                            feature_from=current,
                            feature_to=row
                        )
        if nb_features > 0:
            msg = "{nb} signalement(s) importé(s). ".format(nb=nb_features)
            messages.info(request, msg)

    def check_feature_type_slug(self, request, data, feature_type_slug):
        features = data.get('features', [])
        if len(features) == 0:
            messages.error(
                request,
                "Aucun signalement n'est indiqué dans l'entrée 'features'. ")
            raise IntegrityError

        for feat in features:
            feature_type_import = feat.get('properties', {}).get('feature_type')
            if not feature_type_import:
                messages.error(
                    request,
                    "Le type de signalement doit etre indiqué dans l'entrée 'feature_type' de chaque signalement. ")
                raise IntegrityError

            elif feature_type_import != feature_type_slug:
                messages.error(
                    request,
                    "Le type de signalement ne correspond pas à celui en cours de création: '{dest}'. ".format(
                        dest=feature_type_slug
                    ))
                raise IntegrityError

    @transaction.atomic
    def post(self, request, slug, feature_type_slug):
        feature_type = self.get_object()
        try:
            up_file = request.FILES['json_file'].read()
            data = json.loads(up_file.decode('utf-8'))
        except Exception:
            logger.exception('ImportFromGeoJSON.post')
            messages.error(request, "Erreur à l'import du fichier. ")
        else:
            try:
                with transaction.atomic():
                    self.check_feature_type_slug(request, data, feature_type_slug)
                    self.create_features(request, request.user, data, feature_type)
            except IntegrityError:
                messages.error(request, "Erreur lors de l'import d'un fichier GeoJSON. ")

        return redirect('geocontrib:feature_type_detail', slug=slug, feature_type_slug=feature_type_slug)


@method_decorator(DECORATORS, name='dispatch')
class ImportFromImage(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = FeatureType.objects.all()
    slug_url_kwarg = 'feature_type_slug'

    def test_func(self):
        return True
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
