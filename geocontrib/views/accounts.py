from django.views.generic.base import TemplateView
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View

from api.serializers import ProjectDetailedSerializer
from api.serializers import EventSerializer

from geocontrib.models import Authorization
from geocontrib.models import Event
from geocontrib.models import Project
from geocontrib.models import UserLevelPermission
from geocontrib import choices

DECORATORS = [csrf_exempt, login_required(login_url=settings.LOGIN_URL)]


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


class LoginView(TemplateView):
    """
        Authentification par proxy
    """
    template_name = 'geocontrib/registration/login.html'


class LogoutView(TemplateView):

    template_name = 'geocontrib/registration/login.html'


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
            context['permissions'][project.slug] = Authorization.has_permission(user, 'can_view_project', project)

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
        serilized_projects = ProjectDetailedSerializer(
            Project.objects.filter(
                Q(pk__in=project_authorized) | Q(creator=user)
            ).order_by('-created_on'), many=True)

        all_events = Event.objects.filter(user=user).order_by('-created_on')
        serialized_events = EventSerializer(all_events[0:5], many=True)

        feature_events = Event.objects.filter(user=user, object_type='feature').order_by('-created_on')
        serialized_feature_events = EventSerializer(feature_events[0:5], many=True)

        comment_events = Event.objects.filter(user=user, object_type='comment').order_by('-created_on')
        serialized_comment_events = EventSerializer(comment_events[0:5], many=True)

        context['projects'] = serilized_projects.data
        context['events'] = serialized_events.data
        context['features'] = serialized_feature_events.data
        context['comments'] = serialized_comment_events.data
        context['title'] = "Mon compte"

        return render(request, 'geocontrib/my_account.html', context)
