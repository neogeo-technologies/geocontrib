from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from django.views.decorators.csrf import csrf_exempt

from collab.forms import AuthorizationForm
from collab.forms import CustomFieldModelForm
from collab.forms import CustomFieldModelBaseFS
from collab.forms import CommentForm
from collab.forms import ExtendedBaseFS
from collab.forms import FeatureTypeModelForm
from collab.forms import FeatureDynamicForm
from collab.forms import ProjectModelForm
from collab.models import Authorization
from collab.models import Attachment
from collab.models import Comment
from collab.models import CustomField
# from collab.models import Event
from collab.models import Feature
from collab.models import FeatureType
from collab.models import FeatureLink
from collab.models import Project
from collab.models import UserLevelPermission
from collab.utils import save_custom_fields
from collab.utils import retreive_custom_fields

import logging
logger = logging.getLogger('django')

DECORATORS = [csrf_exempt, login_required(login_url=settings.LOGIN_URL)]

User = get_user_model()

####################
# ATTACHMENT VIEWS #
####################


@method_decorator(DECORATORS, name='dispatch')
class CreateAttachment(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = Feature.objects.all()
    pk_url_kwarg = 'feature_id'

    def test_func(self):
        user = self.request.user
        feature = self.get_object()
        project = feature.project
        return Authorization.has_permission(user, 'can_view_feature', project)

    def post(self, request, slug, feature_type_slug, feature_id):
        feature = self.get_object()
        project = feature.project
        user = request.user
        permissions = Authorization.all_permissions(user, project)
        form = CommentForm(request.POST or None, request.FILE)
        if form.is_valide():
            Attachment.objects.create(
                feature_id=feature.feature_id,
                author=request.user,
                project=project,
                comment=form.cleaned_data.get('comment'),
                feature_type_slug=feature.feature_type.slug,
            )
        context = {
            'feature': feature,
            'feature_type': feature.feature_type,
            'project': project,
            'permissions': permissions,
        }
        return render(request, 'collab/feature/feature.html', context)


#################
# COMMENT VIEWS #
#################


@method_decorator(DECORATORS, name='dispatch')
class CreateComment(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = Feature.objects.all()
    pk_url_kwarg = 'feature_id'

    def test_func(self):
        user = self.request.user
        feature = self.get_object()
        project = feature.project
        return Authorization.has_permission(user, 'can_view_feature', project)

    def post(self, request, slug, feature_type_slug, feature_id):
        feature = self.get_object()
        project = feature.project
        user = request.user
        permissions = Authorization.all_permissions(user, project)
        form = CommentForm(request.POST or None)
        if form.is_valide():
            Comment.objects.create(
                feature_id=feature.feature_id,
                author=request.user,
                project=project,
                comment=form.cleaned_data.get('comment'),
                feature_type_slug=feature.feature_type.slug,
            )
        context = {
            'feature': feature,
            'feature_type': feature.feature_type,
            'project': project,
            'permissions': permissions,
        }
        return render(request, 'collab/feature/feature.html', context)


#################
# FEATURE VIEWS #
#################


@method_decorator(DECORATORS, name='dispatch')
class CreateFeature(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = FeatureType.objects.all()
    slug_url_kwarg = 'feature_type_slug'
    CreateForm = FeatureDynamicForm

    def test_func(self):
        user = self.request.user
        feature_type = self.get_object()
        return Authorization.has_permission(user, 'can_create_feature', feature_type.project)

    def get(self, request, slug, feature_type_slug):
        user = request.user
        feature_type = self.get_object()
        project = feature_type.project
        extra = CustomField.objects.filter(feature_type=feature_type)

        form = self.CreateForm(feature_type=feature_type, extra=extra)

        context = {
            'project': project,
            'feature_type': feature_type,
            'feature_types': project.featuretype_set.all(),
            'permissions': Authorization.all_permissions(user, project),
            'form': form
        }

        return render(request, 'collab/feature/add_feature.html', context)

    def post(self, request, slug, feature_type_slug):

        user = request.user
        feature_type = self.get_object()
        project = feature_type.project
        extra = CustomField.objects.filter(feature_type=feature_type)
        form = self.CreateForm(request.POST, feature_type=feature_type, extra=extra)

        if form.is_valid():
            try:

                Feature.objects.create(
                    title=form.cleaned_data.get('title'),
                    description=form.cleaned_data.get('description'),
                    status=form.cleaned_data.get('status'),
                    geom=form.cleaned_data.get('geom'),
                    project=project,
                    feature_type=feature_type,
                    user=user,
                    feature_data=save_custom_fields(extra, form.cleaned_data)
                )
            except Exception as err:
                messages.error(
                    request,
                    "Une erreur s'est produite lors de la création du signalement {title}: {err}".format(
                        title=form.cleaned_data.get('title', 'N/A'),
                        err=str(err)))
            else:
                messages.info(
                    request,
                    "Le signalement {title} a bien été crée. ".format(
                        title=form.cleaned_data.get('title', 'N/A'),
                    ))
            return redirect('project', slug=project.slug)

        else:
            context = {
                'project': project,
                'feature_type': feature_type,
                'feature_types': project.featuretype_set.all(),
                'permissions': Authorization.all_permissions(user, project),
                'form': form
            }
            return render(request, 'collab/feature/add_feature.html', context)


@method_decorator(DECORATORS, name='dispatch')
class FeatureList(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = Project.objects.all()

    def test_func(self):
        user = self.request.user
        project = self.get_object()
        return Authorization.has_permission(user, 'can_view_feature', project)

    def get(self, request, slug):
        project = self.get_object()
        user = request.user
        permissions = Authorization.all_permissions(user, project)
        features = Feature.objects.filter(project=project).order_by('-status', 'created_on')
        feature_types = FeatureType.objects.filter(project=project)
        context = {
            'features': features,
            'feature_types': feature_types,
            'project': project,
            'permissions': permissions,
            # 'empty_feature_types': FeatureType.objects.filter(
            #     project=project
            # ).exclude(pk__in=[feat.feature_type.pk for feat in features]).values_list('slug', flat=True)
        }

        return render(request, 'collab/feature/feature_list.html', context)


@method_decorator(DECORATORS, name='dispatch')
class FeatureDetail(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = Feature.objects.all()
    pk_url_kwarg = 'feature_id'
    EditForm = FeatureDynamicForm

    def test_func(self):
        user = self.request.user
        feature = self.get_object()
        project = feature.project
        return Authorization.has_permission(user, 'can_view_feature', project)

    def get(self, request, slug, feature_type_slug, feature_id):
        user = request.user
        feature = self.get_object()
        project = feature.project
        feature_type = feature.feature_type
        extra = CustomField.objects.filter(feature_type=feature_type)

        availables_features = Feature.objects.filter(
            project=project,
            # status='published'
        ).exclude(feature_id=feature.feature_id)

        linked_features = FeatureLink.objects.filter(feature_from=feature.feature_id)

        # import pdb; pdb.set_trace()

        form = self.EditForm(instance=feature, feature_type=feature_type, extra=extra)

        # RelatedFormset = formset_factory(
        #     form=FeatureRelatedForm, formset=LocalizedBaseFS, extra=0, can_delete=True)
        # feature_link = models.FeatureLink.objects.filter(feature_from=feature.get('feature_id'))
        # initials = feature_link.annotate(
        #     relation=F('relation_type'),
        #     feature_id=F('feature_to')).values('relation', 'feature_id')
        # formset_related = RelatedFormset(initial=initials)

        context = {
            'feature': feature,
            'feature_types': FeatureType.objects.filter(project=project),
            'feature_type': feature.feature_type,
            'project': project,
            'permissions': Authorization.all_permissions(user, project),
            'form': form,
            'lib_extra': retreive_custom_fields(extra, feature.feature_data),
            'availables_features': availables_features
        }

        return render(request, 'collab/feature/feature.html', context)

    def post(self, request, slug, feature_type_slug, feature_id):

        feature = self.get_object()
        project = feature.project
        feature_type = feature.feature_type

        extra = CustomField.objects.filter(feature_type=feature_type)
        form = self.EditForm(request.POST, feature_type=feature_type, extra=extra)
        if form.is_valid():
            feature.title = form.cleaned_data.get('title')
            feature.description = form.cleaned_data.get('description')
            feature.status = form.cleaned_data.get('status')
            feature.geom = form.cleaned_data.get('geom')
            feature.feature_data = save_custom_fields(extra, form.cleaned_data)
            feature.save()
            # TODO@cbenhabib: a terme mettre dans une methode save du form
            # form.save()
            return HttpResponseRedirect(
                reverse('collab:feature_detail', kwargs={
                    'slug': project.slug,
                    'feature_type_slug': feature_type.slug,
                    'feature_id': feature_id,
                }))

        features = Feature.objects.filter(project=project)
        context = {
            'features': features,
            'feature_types': FeatureType.objects.filter(project=project),
            'project': project,
            'permissions': Authorization.all_permissions(request.user, project),
            'empty_feature_types': FeatureType.objects.filter(
                project=project
            ).exclude(pk__in=[feat.feature_type.pk for feat in features]).values_list('slug', flat=True)
        }
        # return render(request, 'collab/feature/feature.html', context)
        return render(request, 'collab/feature/feature_list.html', context)


class FeatureDelete(DeleteView):
    model = Feature
    pk_url_kwarg = 'feature_id'
    success_url = reverse_lazy('index')


######################
# FEATURE TYPE VIEWS #
######################


@method_decorator(DECORATORS, name='dispatch')
class CreateFeatureType(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = Project.objects.all()
    CustomFieldsFormSet = modelformset_factory(
        CustomField,
        can_delete=True,
        can_order=True,
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
        form = FeatureTypeModelForm()
        formset = self.CustomFieldsFormSet(queryset=CustomField.objects.none())

        context = {
            'form': form,
            'formset': formset,
            'permissions': Authorization.all_permissions(user, project),
            'feature_types': project.featuretype_set.all(),
            'project': project,
        }
        return render(request, 'collab/feature/add_feature_type.html', context)

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
                        position=data.get("ORDER"),
                        label=data.get("label"),
                        name=data.get("name"),
                        field_type=data.get("field_type"),
                    )
            return redirect('project', slug=project.slug)
        else:
            context = {
                'form': form,
                'formset': formset,
                'permissions': Authorization.all_permissions(user, project),
                'feature_types': project.featuretype_set.all(),
                'project': project,
            }
            return render(request, 'collab/feature/add_feature_type.html', context)


#################
# PROJECT VIEWS #
#################


class ProjectDetail(DetailView):

    model = Project

    # TODO@cbenhabib: renommer en project_detail.html
    template_name = "collab/project/project_home.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        project = self.get_object()
        user = self.request.user

        permissions = Authorization.all_permissions(user, project)
        authorizations = Authorization.objects.filter(
            project=project
        ).order_by('created_on')

        comments = Comment.objects.filter(
            project=project
        ).values(
            'author__first_name', 'author__last_name',
            'comment', 'created_on'
        ).order_by('-created_on')[0:3]

        last_features = Feature.objects.filter(
            project=project
        )[0:3]

        context = {
            "authorizations": authorizations,
            "project": project,
            "user": user,
            "comments": comments,
            "features": last_features,
            "permissions": permissions,
            "feature_types": project.featuretype_set.all()
        }

        return context


@method_decorator(DECORATORS, name='dispatch')
class ProjectExtendedDetail(SingleObjectMixin, View):
    queryset = Project.objects.all()

    def get(self, request, slug):
        project = get_object_or_404(Project, slug=slug)
        form = ProjectModelForm(instance=project)
        context = {
            'form': form,
            'permissions': Authorization.all_permissions(request.user, project),
            'feature_types': project.featuretype_set.all()
        }
        return render(request, 'collab/project/admin_project.html', context)

    def post(self, request, slug):
        project = self.get_object()
        form = ProjectModelForm(request.POST, request.FILES, instance=project)
        if form.is_valid() and form.has_changed():
            form.save()
            return HttpResponseRedirect(
                reverse('collab:project', kwargs={'slug': project.slug}))
        context = {
            'form': form,
            'feature_types': project.featuretype_set.all()
        }
        return render(request, 'collab/project/admin_project.html', context)


@method_decorator(DECORATORS, name='dispatch')
class CreateProject(CreateView):

    model = Project

    form_class = ProjectModelForm

    template_name = 'collab/project/project_create.html'

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.is_administrator

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


@method_decorator(DECORATORS, name='dispatch')
class ProjectMap(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = Project.objects.all()

    def test_func(self):
        user = self.request.user
        project = self.get_object()
        return Authorization.has_permission(user, 'can_update_feature', project)

    def get(self, request, slug):
        raise NotImplementedError


@method_decorator(DECORATORS, name='dispatch')
class ProjectMembers(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = Project.objects.all()
    AuthorizationFormSet = modelformset_factory(
        Authorization,
        can_delete=True,
        form=AuthorizationForm,
        formset=ExtendedBaseFS,
        extra=0,
        fields=('first_name', 'last_name', 'username', 'email', 'level'),
    )

    def test_func(self):
        user = self.request.user
        project = self.get_object()
        return Authorization.has_permission(user, 'is_project_administrator', project)

    def get(self, request, slug):
        user = self.request.user
        project = self.get_object()
        formset = self.AuthorizationFormSet(queryset=Authorization.objects.filter(project=project))
        authorised = Authorization.objects.filter(project=project)
        permissions = Authorization.all_permissions(user, project)
        context = {
            "title": "Gestion des membres du projet {}".format(project.title),
            'authorised': authorised,
            'permissions': permissions,
            'formset': formset,
            'feature_types': FeatureType.objects.filter(project=project)
        }

        return render(request, 'collab/project/admin_members.html', context)

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
    
                elif not authorization and not data.get("DELETE"):
                    # On ne crée pas d'utilisateur: il est choisi parmi ceux existants
                    try:
                        user = User.objects.get(
                            username=data["username"],
                            email=data["email"],
                            is_active=True
                        )
                    except User.DoesNotExist:
                        messages.error(request, "Aucun utilisateur ne correspond. ")
                    else:
                        Authorization.objects.create(
                            user=user,
                            project=project,
                            level=data.get('level')
                        )

            return redirect('collab:project_members', slug=slug)

        context = {
            "title": "Gestion des membres du projet {}".format(project.title),
            'authorised': authorised,
            'permissions': permissions,
            'formset': formset,
            'feature_types': FeatureType.objects.filter(project=project)
        }
        return render(request, 'collab/project/admin_members.html', context)
