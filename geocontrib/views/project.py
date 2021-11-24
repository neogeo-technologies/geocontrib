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

    template_name = "geocontrib/project/project_detail.html"

    def get_context_data(self, **kwargs):

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


@method_decorator(DECORATORS, name='dispatch')
class ProjectUpdate(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = Project.objects.all()

    def test_func(self):
        user = self.request.user
        project = self.get_object()
        return Authorization.has_permission(user, 'can_update_project', project)

    def get(self, request, slug):
        project = get_object_or_404(Project, slug=slug)

        form = ProjectModelForm(instance=project)
        context = {
            'form': form,
            'project': project,
            'permissions': Authorization.all_permissions(request.user, project),
            'feature_types': project.featuretype_set.all(),
            'is_suscriber': Subscription.is_suscriber(request.user, project),
            'action': 'update',
            'title': project.title,
        }
        return render(request, 'geocontrib/project/project_edit.html', context)

    def post(self, request, slug):
        project = self.get_object()
        form = ProjectModelForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            return redirect('geocontrib:project', slug=project.slug)

        context = {
            'form': form,
            'project': project,
            'permissions': Authorization.all_permissions(request.user, project),
            'feature_types': project.featuretype_set.all(),
            'is_suscriber': Subscription.is_suscriber(request.user, project),
            'action': 'update',
            'title': project.title,
        }
        return render(request, 'geocontrib/project/project_edit.html', context)


@method_decorator(DECORATORS, name='dispatch')
class ProjectCreate(CreateView):

    model = Project

    form_class = ProjectModelForm

    template_name = 'geocontrib/project/project_edit.html'

    PROJECT_COPY_RELATED = getattr(settings, 'PROJECT_COPY_RELATED', {})

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.is_administrator

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs.update({'create_from': self.request.GET.get('create_from')})
        return kwargs

    def _duplicate_project_related_sets(self, instance, project_template):
        copy_feature_types = self.PROJECT_COPY_RELATED.get('FEATURE_TYPE', False)
        copy_features = self.PROJECT_COPY_RELATED.get('FEATURE', False)
        if project_template and isinstance(project_template, Project) and copy_feature_types:
            for feature_type in project_template.featuretype_set.all():
                # Pour manipuler une copie immuable
                legit_feature_type = FeatureType.objects.get(pk=feature_type.pk)
                feature_type.pk = None
                feature_type.project = instance
                feature_type.save()
                for custom_field in legit_feature_type.customfield_set.all():
                    custom_field.pk = None
                    custom_field.feature_type = feature_type
                    custom_field.save()
                if copy_features:
                    for feature in legit_feature_type.feature_set.all():
                        feature.pk = None
                        feature.created_on = None
                        feature.updated_on = None
                        feature.creator = self.request.user
                        feature.project = instance
                        feature.feature_type = feature_type
                        feature.save()

    def _duplicate_project_base_map(self, instance, project_template):
        copy_related = self.PROJECT_COPY_RELATED.get('BASE_MAP', False)
        if project_template and isinstance(project_template, Project) and copy_related:
            for base_map in project_template.basemap_set.all():
                legit_base_map = BaseMap.objects.get(pk=base_map.pk)
                base_map.pk = None
                base_map.project = instance
                base_map.save()
                for ctx_layer in legit_base_map.contextlayer_set.all():
                    ctx_layer.pk = None
                    ctx_layer.base_map = base_map
                    ctx_layer.save()

    def _duplicate_project_authorization(self, instance, project_template):
        """
        Un signale est deja en place pour appliquer les permissions initiales
        à la creation d'un projet:
        - createur = rank 4
        - autres = rank 1
        Ici on ecrase ces permissions initiales avec celles du projet type parent
        à l'exclusion de la permission relative au créateur de l'instance courante
        """
        copy_related = self.PROJECT_COPY_RELATED.get('AUTHORIZATION', False)
        if project_template and isinstance(project_template, Project) and copy_related:
            for auth in instance.authorization_set.exclude(user=instance.creator):
                auth.level = Authorization.objects.get(
                    user=auth.user, project=project_template).level
                auth.save()

    def _set_thumbnail(self, instance, form, project_template):
        thumbnail = form.cleaned_data.get('thumbnail')
        print("thumbnail ::::::::::::::::::::::::::::::.", thumbnail)
        copy_related = self.PROJECT_COPY_RELATED.get('THUMBNAIL', False)
        if not thumbnail and hasattr(project_template, 'thumbnail') and copy_related:
            instance.thumbnail = project_template.thumbnail
        return instance

    def _set_creator(self, instance):
        instance.creator = self.request.user
        return instance

    def form_valid(self, form):
        slug = form.cleaned_data.get('create_from')
        project_template = Project.objects.filter(slug=slug).first()
        print("project_template", project_template)
        instance = form.save(commit=False)
        self._set_thumbnail(instance, form, project_template)
        self._set_creator(instance)
        instance.save()
        self._duplicate_project_related_sets(instance, project_template)
        self._duplicate_project_base_map(instance, project_template)
        self._duplicate_project_authorization(instance, project_template)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'create'
        context['title'] = "Création d'un projet"
        return context


@method_decorator(DECORATORS, name='dispatch')
class ProjectMapping(BaseMapContextMixin, UserPassesTestMixin, View):

    queryset = Project.objects.all()

    def test_func(self):
        user = self.request.user
        project = self.get_object()
        return Authorization.has_permission(user, 'can_update_project', project)

    def get(self, request, slug):

        user = self.request.user
        project = self.get_object()
        permissions = Authorization.all_permissions(user, project)
        formset = ProjectBaseMapInlineFormset(instance=project)

        context = {**self.get_context_data(), **{
            'project': project,
            'permissions': permissions,
            'formset': formset,
            'title': project.title,
        }}

        return render(request, 'geocontrib/project/project_mapping.html', context)

    def post(self, request, slug):
        user = self.request.user
        project = self.get_object()
        permissions = Authorization.all_permissions(user, project)
        formset = ProjectBaseMapInlineFormset(data=request.POST or None, instance=project)

        if formset.is_valid():
            formset.save()
            messages.success(request, 'Enregistrement effectué.')
            return redirect('geocontrib:project_mapping', slug=project.slug)
        else:
            logger.debug(formset.errors)
            messages.error(request, "L'édition des fonds cartographiques a échoué. ")
            formset = ProjectBaseMapInlineFormset(data=request.POST or None, instance=project)

        context = {**self.get_context_data(), **{
            'project': project,
            'permissions': permissions,
            'formset': formset,
            'title': project.title,
        }}
        return render(request, 'geocontrib/project/project_mapping.html', context)


@method_decorator(DECORATORS, name='dispatch')
class ProjectMembers(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = Project.objects.all()
    AuthorizationFormSet = modelformset_factory(
        Authorization,
        can_delete=True,
        form=AuthorizationForm,
        formset=AuthorizationBaseFS,
        extra=0,
        fields=('first_name', 'last_name', 'username', 'level'),
    )

    def test_func(self):
        user = self.request.user
        project = self.get_object()
        return Authorization.has_permission(user, 'is_project_administrator', project)

    def get(self, request, slug):
        user = self.request.user
        project = self.get_object()
        formset = self.AuthorizationFormSet(
            queryset=Authorization.objects.filter(
                project=project, user__is_active=True
            ).order_by('user__last_name', 'user__first_name', 'user__username')
        )
        authorised = Authorization.objects.filter(project=project)
        permissions = Authorization.all_permissions(user, project)
        context = {
            "title": "Gestion des membres du projet {}".format(project.title),
            'authorised': authorised,
            'permissions': permissions,
            'project': project,
            'formset': formset,
            'feature_types': FeatureType.objects.filter(project=project)
        }

        return render(request, 'geocontrib/project/project_members.html', context)

    def post(self, request, slug):
        user = self.request.user
        project = self.get_object()
        formset = self.AuthorizationFormSet(request.POST or None)
        authorised = Authorization.objects.filter(project=project)
        permissions = Authorization.all_permissions(user, project)
        if formset.is_valid():
            for data in formset.cleaned_data:
                # id contient l'instance si existante
                authorization = data.pop("id", None)
                if data.get("DELETE"):
                    if authorization:
                        # On ne supprime pas l'utilisateur, mais on cache
                        # ses references dans le signalement
                        if not authorization.user.is_superuser:
                            # hide_feature_user(project, user)
                            pass
                        authorization.delete()
                    else:
                        continue

                elif authorization:
                    authorization.level = data.get('level')
                    authorization.save()

            return redirect('geocontrib:project_members', slug=slug)
        else:
            logger.error(formset.errors)
            context = {
                "title": "Gestion des membres du projet {}".format(project.title),
                'authorised': authorised,
                'permissions': permissions,
                'project': project,
                'formset': formset,
                'feature_types': FeatureType.objects.filter(project=project)
            }
            return render(request, 'geocontrib/project/project_members.html', context)


class ProjectTypeListView(TemplateView, UserPassesTestMixin):

    template_name = "geocontrib/project/project_type_list.html"

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.is_administrator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = settings.APPLICATION_NAME
        serilized_projects = ProjectDetailedSerializer(
            Project.objects.filter(is_project_type=True).order_by('-created_on'),
            many=True
        )
        context['projects'] = serilized_projects.data
        return context


@method_decorator(DECORATORS, name='dispatch')
class SubscribingView(SingleObjectMixin, UserPassesTestMixin, View):

    queryset = Project.objects.all()

    def test_func(self):
        user = self.request.user
        project = self.get_object()
        return Authorization.has_permission(user, 'can_view_feature', project)

    def get(self, request, slug, action):
        project = self.get_object()
        user = request.user

        if action.lower() not in ['ajouter', 'annuler']:
            msg = "Erreur de syntaxe dans l'url d'abonnement. "
            logger.error(msg)
            messages.error(request, "Cette action est incorrecte")

        elif action.lower() == 'ajouter':
            obj, _created = Subscription.objects.get_or_create(
                project=project,
            )
            obj.users.add(user)
            obj.save()
            messages.info(request, 'Vous êtes maintenant abonné aux notifications de ce projet. ')

        elif action.lower() == 'annuler':
            try:
                obj = Subscription.objects.get(project=project)
                obj.users.remove(user)
                obj.save()
                messages.info(request, 'Vous ne recevrez plus les notifications de ce projet. ')
            except Exception:
                logger.exception('SubscribingView.get')

        return redirect('geocontrib:project', slug=slug)
