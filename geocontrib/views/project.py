
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView

from api.serializers import CommentSerializer
from api.serializers import ProjectDetailedSerializer
from geocontrib import logger
from geocontrib.forms import AuthorizationBaseFS
from geocontrib.forms import AuthorizationForm
from geocontrib.forms import ProjectModelForm
from geocontrib.forms import ProjectBaseMapInlineFormset
from geocontrib.models import Authorization
from geocontrib.models import BaseMap
from geocontrib.models import Comment
from geocontrib.models import Feature
from geocontrib.models import FeatureType
from geocontrib.models import Project
from geocontrib.models import Subscription
from geocontrib.views.common import BaseMapContextMixin
from geocontrib.views.common import DECORATORS


@method_decorator(DECORATORS[0], name='dispatch')
class ProjectDetail(BaseMapContextMixin, DetailView):

    model = Project

    template_name = "errors/404.html"

    def get_context_data(self, **kwargs):
        import pdb; pdb.set_trace()

        user = self.request.user
        project = self.get_object()
        permissions = Authorization.all_permissions(user, project)

        # On filtre les signalements selon leur statut et l'utilisateur courant
        features = Feature.handy.availables(
            user=user,
            project=project
        ).order_by('-created_on')

        # On filtre les commentaire selon les signalements visibles
        last_comments = Comment.objects.filter(
            project=project,
            feature_id__in=[feat.feature_id for feat in features]
        ).order_by('-created_on')[0:5]

        serialized_comments = CommentSerializer(last_comments, many=True).data

        serilized_projects = ProjectDetailedSerializer(project).data

        context = super().get_context_data(**kwargs)

        context['project'] = serilized_projects
        context['title'] = project.title
        context['user'] = user
        context['last_comments'] = serialized_comments
        context['last_features'] = features[0:5]
        context['features'] = features
        context['permissions'] = permissions
        context['feature_types'] = project.featuretype_set.all()
        context['is_suscriber'] = Subscription.is_suscriber(user, project)
        return context