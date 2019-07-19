from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import F
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
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
from collab.forms import AttachmentForm
from collab.forms import CommentForm
from collab.forms import ExtendedBaseFS
from collab.forms import FeatureTypeModelForm
from collab.forms import FeatureDynamicForm
from collab.forms import FeatureLinkForm
from collab.forms import ProjectModelForm
from collab.models import Authorization
from collab.models import Attachment
from collab.models import Comment
from collab.models import CustomField
from collab.models import Feature
from collab.models import FeatureType
from collab.models import FeatureLink
from collab.models import Project
from collab.utils import save_custom_fields

import logging
logger = logging.getLogger('django')

DECORATORS = [csrf_exempt, login_required(login_url=settings.LOGIN_URL)]

User = get_user_model()

####################
# ATTACHMENT VIEWS #
####################


@method_decorator(DECORATORS, name='dispatch')
class AttachmentCreate(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = Feature.objects.all()
    pk_url_kwarg = 'feature_id'

    def test_func(self):
        user = self.request.user
        feature = self.get_object()
        project = feature.project
        return Authorization.has_permission(user, 'can_update_feature', project, feature)

    def post(self, request, slug, feature_type_slug, feature_id):
        feature = self.get_object()
        project = feature.project
        user = request.user
        form = AttachmentForm(request.POST or None, request.FILES)
        if form.is_valid():
            try:
                Attachment.objects.create(
                    feature_id=feature.feature_id,
                    author=user,
                    project=project,
                    type_objet='feature',
                    attachment_file=form.cleaned_data.get('attachment_file')
                )
            except Exception as err:
                messages.error(
                    request,
                    "Erreur à l'ajout de la pièce jointe: {err}".format(err=str(err)))
            else:
                messages.info(request, "Ajout de la pièce jointe confirmé")
        else:
            messages.error(request, "Erreur à l'ajout de la pièce jointe")

        return redirect(
            'collab:feature_update', slug=slug,
            feature_type_slug=feature_type_slug, feature_id=feature_id)


#################
# COMMENT VIEWS #
#################


@method_decorator(DECORATORS, name='dispatch')
class CommentCreate(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = Feature.objects.all()
    pk_url_kwarg = 'feature_id'

    def test_func(self):
        user = self.request.user
        feature = self.get_object()
        project = feature.project
        return Authorization.has_permission(user, 'can_view_feature', project, feature)

    def post(self, request, slug, feature_type_slug, feature_id):
        feature = self.get_object()
        project = feature.project
        user = request.user
        form = CommentForm(request.POST, request.FILES)

        linked_features = FeatureLink.objects.filter(
            feature_from=feature.feature_id
        )

        if form.is_valid():
            try:
                comment = Comment.objects.create(
                    feature_id=feature.feature_id,
                    feature_type_slug=feature.feature_type.slug,
                    author=user,
                    project=project,
                    comment=form.cleaned_data.get('comment')
                )
                up_file = form.cleaned_data.get('attachment_file')
                title = form.cleaned_data.get('title')
                info = form.cleaned_data.get('info')
                if comment and up_file and title:
                    Attachment.objects.create(
                        feature_id=feature.feature_id,
                        author=user,
                        project=project,
                        comment=comment,
                        attachment_file=up_file,
                        title=title,
                        info=info,
                        type_objet='comment'
                    )

            except Exception as err:
                logger.error(err)
                messages.error(
                    request,
                    "Erreur à l'ajout du commentaire: {err}".format(err=err))
            else:
                messages.info(request, "Ajout du commentaire confirmé")

            return redirect(
                'collab:feature_detail',
                slug=slug,
                feature_type_slug=feature_type_slug,
                feature_id=feature_id)
        else:
            logger.error(form.errors)

        context = {
            'feature': feature,
            'feature_data': feature.custom_fields_as_list,
            'feature_types': FeatureType.objects.filter(project=project),
            'feature_type': feature.feature_type,
            'linked_features': linked_features,
            'project': project,
            'permissions': Authorization.all_permissions(user, project),
            'comments': Comment.objects.filter(project=project, feature_id=feature.feature_id),
            'attachments': Attachment.objects.filter(project=project, feature_id=feature.feature_id),
            'comment_form': form

        }
        return render(request, 'collab/feature/feature_detail.html', context)


#################
# FEATURE VIEWS #
#################


@method_decorator(DECORATORS, name='dispatch')
class FeatureCreate(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = FeatureType.objects.all()
    slug_url_kwarg = 'feature_type_slug'

    def test_func(self):
        user = self.request.user
        feature_type = self.get_object()
        return Authorization.has_permission(user, 'can_create_feature', feature_type.project)

    def get(self, request, slug, feature_type_slug):
        user = request.user
        feature_type = self.get_object()
        project = feature_type.project
        extra = CustomField.objects.filter(feature_type=feature_type)

        form = FeatureDynamicForm(feature_type=feature_type, extra=extra, user=user)

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
        form = FeatureDynamicForm(
            request.POST, feature_type=feature_type, extra=extra, user=user)
        if form.is_valid():
            try:
                feature = Feature.objects.create(
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
                return redirect(
                    'collab:feature_detail', slug=project.slug,
                    feature_type_slug=feature_type.slug, feature_id=feature.feature_id)

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
        feature_types = FeatureType.objects.filter(project=project)
        context = {
            'features': Feature.handy.availables(user, project).order_by('-status', 'created_on'),
            'feature_types': feature_types,
            'project': project,
            'permissions': permissions,
        }

        return render(request, 'collab/feature/feature_list.html', context)


@method_decorator(DECORATORS, name='dispatch')
class FeatureDetail(SingleObjectMixin, UserPassesTestMixin, View):

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

        linked_features = FeatureLink.objects.filter(
            feature_from=feature.feature_id
        )

        context = {
            'feature': feature,
            'feature_data': feature.custom_fields_as_list,
            'feature_types': FeatureType.objects.filter(project=project),
            'feature_type': feature.feature_type,
            'linked_features': linked_features,
            'project': project,
            'permissions': Authorization.all_permissions(user, project, feature),
            'comments': Comment.objects.filter(project=project, feature_id=feature.feature_id),
            'comment_form': CommentForm(),
            'attachment_form': AttachmentForm(),
        }

        return render(request, 'collab/feature/feature_detail.html', context)


@method_decorator(DECORATORS, name='dispatch')
class FeatureUpdate(SingleObjectMixin, UserPassesTestMixin, View):

    queryset = Feature.objects.all()
    pk_url_kwarg = 'feature_id'
    LinkedFormset = modelformset_factory(
        model=FeatureLink,
        form=FeatureLinkForm,
        extra=0,
        can_delete=True)

    def test_func(self):
        user = self.request.user
        feature = self.get_object()
        project = feature.project
        return Authorization.has_permission(user, 'can_update_feature', project, feature)

    def get(self, request, slug, feature_type_slug, feature_id):

        user = request.user
        feature = self.get_object()
        project = feature.project
        feature_type = feature.feature_type
        extra = CustomField.objects.filter(feature_type=feature_type)

        availables_features = Feature.objects.filter(
            project=project,
        ).exclude(feature_id=feature.feature_id)

        form = FeatureDynamicForm(
            instance=feature, feature_type=feature_type, extra=extra, user=user)

        linked_features = FeatureLink.objects.filter(
            feature_from=feature.feature_id
        ).annotate(
            feature_id=F('feature_to')).values('relation_type', 'feature_id')

        linked_formset = self.LinkedFormset(
            initial=linked_features,
            queryset=FeatureLink.objects.filter(feature_from=feature.feature_id))

        context = {
            'feature': feature,
            'feature_types': FeatureType.objects.filter(project=project),
            'feature_type': feature.feature_type,
            'project': project,
            'permissions': Authorization.all_permissions(user, project, feature),
            'form': form,
            'availables_features': availables_features,
            'linked_formset': linked_formset,
            'attachment_form': AttachmentForm(),
            'comment_form': CommentForm(),
            'attachments': Attachment.objects.filter(
                project=project, feature_id=feature.feature_id,
                type_objet='feature'),
        }
        return render(request, 'collab/feature/feature_update.html', context)

    def post(self, request, slug, feature_type_slug, feature_id):
        user = request.user
        feature = self.get_object()
        project = feature.project
        feature_type = feature.feature_type
        availables_features = Feature.objects.filter(
            project=project,
        ).exclude(feature_id=feature.feature_id)

        extra = CustomField.objects.filter(feature_type=feature_type)
        form = FeatureDynamicForm(
            request.POST, instance=feature, feature_type=feature_type,
            extra=extra, user=user)

        linked_formset = self.LinkedFormset(request.POST)

        if not form.is_valid() or not linked_formset.is_valid():
            messages.error(request, "Erreur à la mise à jour du signalement. ")
            context = {
                'feature': feature,
                'feature_types': FeatureType.objects.filter(project=project),
                'feature_type': feature.feature_type,
                'project': project,
                'permissions': Authorization.all_permissions(user, project),
                'form': form,
                'availables_features': availables_features,
                'linked_formset': linked_formset,
                'attachments': Attachment.objects.filter(
                    project=project, feature_id=feature.feature_id,
                    type_objet='feature'),
            }
            return render(request, 'collab/feature/feature_update.html', context)
        else:
            form.save()
            for data in linked_formset.cleaned_data:
                feature_to = data.get('feature_to')

                if feature_to:
                    if not data.get('DELETE'):
                        FeatureLink.objects.get_or_create(
                            relation_type=data.get('relation_type'),
                            feature_from=feature_id,
                            feature_to=feature_to
                        )
                    if data.get('DELETE'):
                        qs = FeatureLink.objects.filter(
                            relation_type=data.get('relation_type'),
                            feature_from=feature_id,
                            feature_to=feature_to
                        )
                        for instance in qs:
                            instance.delete()

        return redirect(
            'collab:feature_detail', slug=project.slug,
            feature_type_slug=feature_type.slug, feature_id=feature.feature_id)


class FeatureDelete(DeleteView):
    model = Feature
    pk_url_kwarg = 'feature_id'
    success_url = reverse_lazy('collab:index')


######################
# FEATURE TYPE VIEWS #
######################


@method_decorator(DECORATORS, name='dispatch')
class FeatureTypeCreate(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = Project.objects.all()
    CustomFieldsFormSet = modelformset_factory(
        CustomField,
        can_delete=True,
        # can_order=True,
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
        return render(request, 'collab/feature_type/feature_type_create.html', context)

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
                    )
            return redirect('collab:project', slug=project.slug)
        else:
            context = {
                'form': form,
                'formset': formset,
                'permissions': Authorization.all_permissions(user, project),
                'feature_types': project.featuretype_set.all(),
                'project': project,
            }
            return render(request, 'collab/feature/add_feature_type.html', context)


@method_decorator(DECORATORS, name='dispatch')
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

        context = {
            'feature_type': feature_type,
            'permissions': Authorization.all_permissions(user, project),
            'feature_types': project.featuretype_set.all(),
            'project': project,
            'structure': {'todo': 'Ajout de structure'}
        }

        return render(request, 'collab/feature_type/feature_type_detail.html', context)

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

        context['authorizations'] = authorizations
        context['project'] = project
        context['user'] = user
        context['comments'] = comments
        context['features'] = last_features
        context['permissions'] = permissions
        context['feature_types'] = project.featuretype_set.all()
        return context


@method_decorator(DECORATORS, name='dispatch')
class ProjectUpdate(SingleObjectMixin, View):
    queryset = Project.objects.all()

    def get(self, request, slug):
        project = get_object_or_404(Project, slug=slug)
        form = ProjectModelForm(instance=project)
        context = {
            'form': form,
            'permissions': Authorization.all_permissions(request.user, project),
            'feature_types': project.featuretype_set.all(),
            'action': 'update'
        }
        return render(request, 'collab/project/project_edit.html', context)

    def post(self, request, slug):
        project = self.get_object()
        form = ProjectModelForm(request.POST, request.FILES, instance=project)
        if form.is_valid() and form.has_changed():
            form.save()
            return redirect('collab:project', slug=project.slug)

        context = {
            'form': form,
            'feature_types': project.featuretype_set.all()
        }
        return render(request, 'collab/project/project_edit.html', context)


@method_decorator(DECORATORS, name='dispatch')
class ProjectCreate(CreateView):

    model = Project

    form_class = ProjectModelForm

    template_name = 'collab/project/project_edit.html'

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.is_administrator

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'create'
        return context

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
        """

        """
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
                    # TODO @cbenhabib: A brancher sur proxy cas
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
