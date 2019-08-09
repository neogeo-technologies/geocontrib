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

from collab.models import Authorization
from collab.models import Event
from collab.models import Project
from collab.models import UserLevelPermission
from collab import choices

DECORATORS = [csrf_exempt, login_required(login_url=settings.LOGIN_URL)]


class HomePageView(TemplateView):

    template_name = "collab/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Collab"

        context["can_create_project"] = False
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser or user.is_administrator:
                context["can_create_project"] = True

        serilized_projects = ProjectDetailedSerializer(
            Project.objects.all().order_by('-created_on'), many=True)

        context['projects'] = serilized_projects.data

        events = Event.objects.filter(user=user).order_by('-created_on')
        serialized_events = EventSerializer(events, many=True)

        context['events'] = serialized_events.data

        return context


class LoginView(TemplateView):
    """
        Authentification par proxy
    """
    template_name = 'collab/registration/login.html'


class LogoutView(TemplateView):

    template_name = 'collab/registration/login.html'


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

        events = Event.objects.filter(user=user).order_by('-created_on')
        serialized_events = EventSerializer(events, many=True)

        context['projects'] = serilized_projects.data
        context['events'] = serialized_events.data

        return render(request, 'collab/my_account.html', context)


def site_help(request):
    context = {"title": "Aide"}
    return render(request, 'collab/help.html', context)


def legal(request):
    context = {"title": "Mentions légales"}
    return render(request, 'collab/legal.html', context)
