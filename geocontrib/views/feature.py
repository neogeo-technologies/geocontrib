from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from api.serializers import EventSerializer
from api.serializers import FeatureLinkSerializer
from geocontrib.forms import CommentForm
from geocontrib.models import Attachment
from geocontrib.models import Authorization
from geocontrib.models import Event
from geocontrib.models import Feature
from geocontrib.models import FeatureLink
from geocontrib.views.common import BaseMapContextMixin
from geocontrib.views.common import DECORATORS

@method_decorator(DECORATORS[0], name='dispatch')
class FeatureDetail(BaseMapContextMixin, UserPassesTestMixin, View):

    queryset = Feature.objects.all()
    pk_url_kwarg = 'feature_id'

    def test_func(self):
        user = self.request.user
        feature = self.get_object()
        project = feature.project
        return Authorization.has_permission(user, 'can_view_feature', project, feature)

    def get(self, request, slug, feature_type_slug, feature_id):
        user = request.user
        feature = self.get_object()
        project = feature.project

        linked_features = FeatureLink.handy.related(
            feature.feature_id
        )
        serialized_link = FeatureLinkSerializer(linked_features, many=True)
        events = Event.objects.filter(feature_id=feature.feature_id).order_by('created_on')
        serialized_events = EventSerializer(events, many=True)

        context = self.get_context_data(feature_id=feature_id)
        context['feature'] = feature
        context['feature_data'] = feature.custom_fields_as_list
        context['linked_features'] = serialized_link.data
        context['permissions'] = Authorization.all_permissions(user, project, feature)
        context['events'] = serialized_events.data
        context['attachments'] = Attachment.objects.filter(
            project=project, feature_id=feature.feature_id, object_type='feature')
        context['comment_form'] = CommentForm()
        context['project'] = project
        return render(request, 'geocontrib/feature/feature_detail.html', context)
