from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.detail import SingleObjectMixin

from api.serializers import FeatureTypeSerializer
from geocontrib.models import Authorization
from geocontrib.models import Feature
from geocontrib.models import FeatureType
from geocontrib.views.common import DECORATORS
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
