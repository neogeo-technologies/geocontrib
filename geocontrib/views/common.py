from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.views.generic.detail import SingleObjectMixin

from api.serializers import BaseMapSerializer
from api.serializers import EventSerializer
from api.serializers import FeatureDetailedSerializer
from api.serializers import LayerSerializer
from api.serializers import ProjectDetailedSerializer
from geocontrib import choices
from geocontrib import logger
from geocontrib.models import Authorization
from geocontrib.models import BaseMap
from geocontrib.models import Event
from geocontrib.models import Feature
from geocontrib.models import FeatureType
from geocontrib.models import Layer
from geocontrib.models import Project
from geocontrib.models import UserLevelPermission


DECORATORS = [csrf_exempt, login_required(login_url=settings.LOGIN_URL)]


class BaseMapContextMixin(SingleObjectMixin):

    def get_context_data(self, feature_id=None, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        try:
            request = self.request
            project = None
            title = None
            if any([isinstance(self.object, model) for model in [Project, FeatureType, Feature]]):
                title = self.object.title
            if isinstance(self.object, Project):
                project = self.object
            elif isinstance(self.object, FeatureType) or isinstance(self.object, Feature):
                project = self.object.project

            serialized_base_maps = BaseMapSerializer(
                BaseMap.objects.filter(project=project),
                many=True
            )
            serialized_layers = LayerSerializer(
                Layer.objects.all(),
                many=True
            )
            features = Feature.handy.availables(user=self.request.user, project=project)

            if feature_id:
                features = features.filter(feature_id=feature_id)

            serialized_features = FeatureDetailedSerializer(
                features,
                is_authenticated=request.user.is_authenticated,
                context={'request': request},
                many=True
            )
            import pdb; pdb.set_trace()
            context['serialized_features'] = serialized_features.data
            context['serialized_base_maps'] = serialized_base_maps.data
            context['serialized_layers'] = serialized_layers.data
            context['title'] = title
        except Exception:
            logger.exception('BaseMapContext error')
        return context


class HomePageView(TemplateView):

    template_name = "geocontrib/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = settings.APPLICATION_NAME

        context["can_create_project"] = False
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser or user.is_administrator:
                context["can_create_project"] = True

        serilized_projects = ProjectDetailedSerializer(
            Project.objects.all().order_by('-created_on'), many=True)

        context['projects'] = serilized_projects.data

        return context


@method_decorator(DECORATORS, name='dispatch')
class MyAccount(View):

    def get(self, request):
        context = {}
        user = request.user
        # context['user'] = user

        # on liste les droits de l'utilisateur pour chaque projet
        context['permissions'] = {}
        context['rank'] = {}
        for project in Project.objects.all():
            context['permissions'][project.slug] = Authorization.has_permission(
                user, 'can_view_project', project)

            try:
                rank = Authorization.objects.get(project=project, user=user).level
            except Exception:
                if user.is_superuser:
                    usertype = choices.ADMIN
                else:
                    usertype = choices.LOGGED_USER
                rank = UserLevelPermission.objects.get(user_type_id=usertype)

            context['rank'][project.slug] = rank

        project_authorized = Authorization.objects.filter(
            user=user
        ).filter(
            level__rank__lte=2
        ).values_list('project__pk', flat=True)
        serialized_projects = ProjectDetailedSerializer(
            Project.objects.filter(
                Q(pk__in=project_authorized) | Q(creator=user)
            ).order_by('-created_on'), many=True)

        all_events = Event.objects.filter(user=user).order_by('-created_on')
        serialized_events = EventSerializer(all_events[0:5], many=True)

        feature_events = Event.objects.filter(
            user=user, object_type='feature').order_by('-created_on')
        serialized_feature_events = EventSerializer(feature_events[0:5], many=True)

        comment_events = Event.objects.filter(
            user=user, object_type='comment').order_by('-created_on')
        serialized_comment_events = EventSerializer(comment_events[0:5], many=True)

        context['projects'] = serialized_projects.data
        context['events'] = serialized_events.data
        context['features'] = serialized_feature_events.data
        context['comments'] = serialized_comment_events.data
        context['title'] = "Mon compte"

        return render(request, 'geocontrib/my_account.html', context)
