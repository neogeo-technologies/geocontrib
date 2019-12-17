import json
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos.error import GEOSException
from django.db import IntegrityError, transaction
from django.db.models import F
from django.forms import modelformset_factory
from django.http import JsonResponse
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

from api.serializers import CommentSerializer
from api.serializers import EventSerializer
from api.serializers import FeatureLinkSerializer
from api.serializers import FeatureTypeSerializer
from api.serializers import LayerSerializer
from api.serializers import ProjectDetailedSerializer

from collab.exif import exif
from collab.forms import AuthorizationForm
from collab.forms import AuthorizationBaseFS
from collab.forms import CustomFieldModelForm
from collab.forms import CustomFieldModelBaseFS
from collab.forms import AttachmentForm
from collab.forms import CommentForm
from collab.forms import FeatureTypeModelForm
from collab.forms import FeatureBaseForm
from collab.forms import FeatureExtraForm
from collab.forms import FeatureLinkForm
from collab.forms import LayerForm
from collab.forms import ProjectModelForm
from collab.models import Authorization
from collab.models import Attachment
from collab.models import Comment
from collab.models import CustomField
from collab.models import Event
from collab.models import Feature
from collab.models import FeatureType
from collab.models import FeatureLink
from collab.models import Layer
from collab.models import Project
from collab.models import Subscription

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
                    object_type='feature',
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
        return Authorization.has_permission(user, 'can_create_feature', project)

    def post(self, request, slug, feature_type_slug, feature_id):
        feature = self.get_object()
        project = feature.project
        user = request.user
        form = CommentForm(request.POST, request.FILES)

        linked_features = FeatureLink.objects.filter(
            feature_from=feature.feature_id
        )
        serialized_link = FeatureLinkSerializer(linked_features, many=True)

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
                        object_type='comment'
                    )

            except Exception as err:
                logger.exception('CommentCreate.post')
                messages.error(
                    request,
                    "Erreur à l'ajout du commentaire: {err}".format(err=err))
            else:
                # Un evenement est ajouter lors de la creation d'un commentaire
                # au niveau des trigger.
                messages.info(request, "Ajout du commentaire confirmé")

            return redirect(
                'collab:feature_detail',
                slug=slug,
                feature_type_slug=feature_type_slug,
                feature_id=feature_id)
        else:
            logger.error(form.errors)

        events = Event.objects.filter(feature_id=feature.feature_id).order_by('created_on')
        serialized_events = EventSerializer(events, many=True)

        context = {
            'feature': feature,
            'feature_data': feature.custom_fields_as_list,
            'feature_types': FeatureType.objects.filter(project=project),
            'feature_type': feature.feature_type,
            'linked_features': serialized_link.data,
            'project': project,
            'permissions': Authorization.all_permissions(user, project, feature),
            'comments': Comment.objects.filter(project=project, feature_id=feature.feature_id),
            'attachments': Attachment.objects.filter(
                project=project, feature_id=feature.feature_id, object_type='feature'),
            'events': serialized_events.data,
            'comment_form': CommentForm(),
        }

        return render(request, 'collab/feature/feature_detail.html', context)


#################
# FEATURE VIEWS #
#################


@method_decorator(DECORATORS, name='dispatch')
class FeatureCreate(SingleObjectMixin, UserPassesTestMixin, View):
    """
        TODO @cbenhabib: les vues FeatureCreate et FeatureUpdate doivent etre mergées.
    """
    queryset = FeatureType.objects.all()
    slug_url_kwarg = 'feature_type_slug'

    LinkedFormset = modelformset_factory(
        model=FeatureLink,
        form=FeatureLinkForm,
        extra=0,
        can_delete=True)

    AttachmentFormset = modelformset_factory(
        model=Attachment,
        form=AttachmentForm,
        extra=0,
        can_delete=True)

    def test_func(self):
        user = self.request.user
        feature_type = self.get_object()
        return Authorization.has_permission(user, 'can_create_feature', feature_type.project)

    def get(self, request, slug, feature_type_slug):
        user = request.user
        feature_type = self.get_object()
        project = feature_type.project
        layers = Layer.objects.filter(project=project)
        serialized_layers = LayerSerializer(layers, many=True)
        extra = CustomField.objects.filter(feature_type=feature_type)

        feature_form = FeatureBaseForm(
            feature_type=feature_type, user=user)

        extra_form = FeatureExtraForm(extra=extra)

        linked_formset = self.LinkedFormset(
            form_kwargs={'feature_type': feature_type},
            prefix='linked',
            queryset=FeatureLink.objects.none()
        )

        attachment_formset = self.AttachmentFormset(
            prefix='attachment',
            queryset=Attachment.objects.none()
        )

        context = {
            'features': Feature.handy.availables(user, project).order_by('updated_on'),
            'feature_type': feature_type,
            'project': project,
            'feature_form': feature_form,
            'extra_form': extra_form,
            'linked_formset': linked_formset,
            'attachment_formset': attachment_formset,
            'action': 'create',
            'layers': serialized_layers.data
        }
        return render(request, 'collab/feature/feature_edit.html', context)

    def post(self, request, slug, feature_type_slug):

        user = request.user
        feature_type = self.get_object()
        project = feature_type.project
        layers = Layer.objects.filter(project=project)
        serialized_layers = LayerSerializer(layers, many=True)
        feature_form = FeatureBaseForm(
            request.POST, feature_type=feature_type, user=user)
        extra = CustomField.objects.filter(feature_type=feature_type)
        extra_form = FeatureExtraForm(request.POST, extra=extra)

        linked_formset = self.LinkedFormset(
            request.POST or None,
            prefix='linked',
            form_kwargs={'feature_type': feature_type},
        )

        attachment_formset = self.AttachmentFormset(
            request.POST or None, request.FILES, prefix='attachment')

        all_forms = [
            feature_form,
            extra_form,
            attachment_formset,
            linked_formset,
        ]

        forms_are_valid = all([ff.is_valid() for ff in all_forms])

        if forms_are_valid:
            try:
                feature = feature_form.save(
                    project=project,
                    feature_type=feature_type,
                    creator=user,
                    extra=extra_form.cleaned_data
                )
            except Exception as err:
                logger.exception('FeatureCreate.post')
                messages.error(
                    request,
                    "Une erreur s'est produite lors de la création du signalement {title}: {err}".format(
                        title=feature_form.cleaned_data.get('title', 'N/A'),
                        err=str(err)))
            else:

                # Traitement des signalements liés
                for data in linked_formset.cleaned_data:

                    feature_link = data.pop('id', None)

                    if feature_link:
                        if not data.get('DELETE'):
                            feature_link.relation_type = data.get('relation_type')
                            feature_link.feature_to = data.get('feature_to')
                            feature_link.save()

                        if data.get('DELETE'):
                            feature_link.delete()

                    if not feature_link and not data.get('DELETE'):
                        FeatureLink.objects.create(
                            relation_type=data.get('relation_type'),
                            feature_from=feature.feature_id,
                            feature_to=data.get('feature_to')
                        )

                # Traitement des piéces jointes
                for data in attachment_formset.cleaned_data:

                    attachment = data.pop('id', None)

                    if attachment and data.get('DELETE'):
                        attachment.delete()

                    if attachment and not data.get('DELETE'):
                        attachment.attachment_file = data.get('attachment_file')
                        attachment.title = data.get('title')
                        attachment.info = data.get('info')
                        attachment.save()

                    if not attachment and not data.get('DELETE'):
                        Attachment.objects.create(
                            attachment_file=data.get('attachment_file'),
                            title=data.get('title'),
                            info=data.get('info'),
                            object_type='feature',
                            project=project,
                            feature_id=feature.feature_id,
                            author=user,
                        )

                messages.info(
                    request,
                    "Le signalement {title} a bien été créé. ".format(
                        title=feature.title,
                    ))

                return redirect(
                    'collab:feature_detail', slug=project.slug,
                    feature_type_slug=feature_type.slug, feature_id=feature.feature_id)

        else:
            logger.error([ff.errors for ff in all_forms])

        linked_formset = self.LinkedFormset(
            request.POST or None,
            prefix='linked',
            form_kwargs={'feature_type': feature_type},
        )

        attachment_formset = self.AttachmentFormset(
            request.POST or None, request.FILES, prefix='attachment')

        context = {
            'features': Feature.handy.availables(user, project).order_by('updated_on'),
            'feature_type': feature_type,
            'project': project,
            # 'permissions': Authorization.all_permissions(user, project),
            'feature_form': feature_form,
            'extra_form': extra_form,
            'linked_formset': linked_formset,
            'attachment_formset': attachment_formset,
            'action': 'create',
            'layers': serialized_layers.data
        }
        return render(request, 'collab/feature/feature_edit.html', context)


@method_decorator(DECORATORS[0], name='dispatch')
class FeatureList(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = Project.objects.all()

    def test_func(self):
        user = self.request.user
        project = self.get_object()
        return Authorization.has_permission(user, 'can_view_feature', project)

    def get(self, request, slug, *args, **kwargs):

        project = self.get_object()
        user = request.user
        layers = Layer.objects.filter(project=project).order_by('order')
        serialized_layers = LayerSerializer(layers, many=True)
        permissions = Authorization.all_permissions(user, project)
        feature_types = FeatureType.objects.filter(project=project)
        features = Feature.handy.availables(user, project).order_by('-updated_on')

        filters = {}
        filters['status'] = request.GET.get('status', None)
        filters['feature_type__slug'] = request.GET.get('feature_type', None)
        filters['title__icontains'] = request.GET.get('title', None)
        if filters:
            filters = {k: v for k, v in filters.items() if v is not None}
            features = features.filter(**filters)

        context = {
            'features': features,
            'feature_types': feature_types,
            'layers': serialized_layers.data,
            'project': project,
            'permissions': permissions,
            'status_choices': Feature.STATUS_CHOICES,
        }

        return render(request, 'collab/feature/feature_list.html', context)


@method_decorator(DECORATORS[0], name='dispatch')
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
        layers = Layer.objects.filter(project=project)
        serialized_layers = LayerSerializer(layers, many=True)

        linked_features = FeatureLink.objects.filter(
            feature_from=feature.feature_id
        )
        serialized_link = FeatureLinkSerializer(linked_features, many=True)

        events = Event.objects.filter(feature_id=feature.feature_id).order_by('created_on')
        serialized_events = EventSerializer(events, many=True)

        context = {
            'feature': feature,
            'feature_data': feature.custom_fields_as_list,
            'feature_types': FeatureType.objects.filter(project=project),
            'feature_type': feature.feature_type,
            'linked_features': serialized_link.data,
            'project': project,
            'permissions': Authorization.all_permissions(user, project, feature),
            'comments': Comment.objects.filter(project=project, feature_id=feature.feature_id),
            'attachments': Attachment.objects.filter(
                project=project, feature_id=feature.feature_id, object_type='feature'),
            'events': serialized_events.data,
            'comment_form': CommentForm(),
            'layers': serialized_layers.data,
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

    AttachmentFormset = modelformset_factory(
        model=Attachment,
        form=AttachmentForm,
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
        layers = Layer.objects.filter(project=project)
        serialized_layers = LayerSerializer(layers, many=True)
        extra = CustomField.objects.filter(feature_type=feature_type)

        availables_features = Feature.objects.filter(
            project=project,
        ).exclude(feature_id=feature.feature_id)

        feature_form = FeatureBaseForm(
            instance=feature, feature_type=feature_type, user=user)

        extra_form = FeatureExtraForm(feature=feature, extra=extra)

        linked_features = FeatureLink.objects.filter(
            feature_from=feature.feature_id
        ).annotate(
            feature_id=F('feature_to')).values('relation_type', 'feature_id')

        linked_formset = self.LinkedFormset(
            form_kwargs={'feature_type': feature_type, 'feature': feature},
            prefix='linked',
            initial=linked_features,
            queryset=FeatureLink.objects.filter(feature_from=feature.feature_id))

        attachments = Attachment.objects.filter(
            project=project, feature_id=feature.feature_id,
            object_type='feature'
        )

        attachment_formset = self.AttachmentFormset(
            prefix='attachment',
            initial=attachments.values(),
            queryset=attachments
        )

        context = {
            'feature': feature,
            'features': Feature.handy.availables(user, project).order_by('updated_on'),
            'feature_data': feature.custom_fields_as_list,
            'feature_types': FeatureType.objects.filter(project=project),
            'feature_type': feature.feature_type,
            'project': project,
            'permissions': Authorization.all_permissions(user, project, feature),
            'feature_form': feature_form,
            'extra_form': extra_form,
            'availables_features': availables_features,
            'linked_formset': linked_formset,
            'attachment_formset': attachment_formset,
            'attachments': attachments,
            'action': 'update',
            'layers': serialized_layers.data
        }
        return render(request, 'collab/feature/feature_edit.html', context)

    def post(self, request, slug, feature_type_slug, feature_id):
        user = request.user
        feature = self.get_object()
        project = feature.project
        feature_type = feature.feature_type
        availables_features = Feature.handy.availables(
            user=user,
            project=project,
        ).exclude(
            feature_id=feature.feature_id
        )
        layers = Layer.objects.filter(project=project)
        serialized_layers = LayerSerializer(layers, many=True)
        extra = CustomField.objects.filter(feature_type=feature_type)

        feature_form = FeatureBaseForm(
            request.POST, instance=feature, feature_type=feature_type, user=user)

        extra_form = FeatureExtraForm(request.POST, feature=feature, extra=extra)

        linked_formset = self.LinkedFormset(
            request.POST or None,
            prefix='linked',
            form_kwargs={'feature_type': feature_type, 'feature': feature},
            queryset=FeatureLink.objects.filter(feature_from=feature.feature_id))

        attachments = Attachment.objects.filter(
            project=project, feature_id=feature.feature_id,
            object_type='feature'
        )

        attachment_formset = self.AttachmentFormset(
            request.POST or None, request.FILES, prefix='attachment')

        old_status = feature.status

        old_geom = feature.geom.wkt if feature.geom else ''

        all_forms = [
            feature_form,
            extra_form,
            attachment_formset,
            linked_formset,
        ]

        forms_are_valid = all([ff.is_valid() for ff in all_forms])

        if not forms_are_valid:
            logger.error([ff.errors for ff in all_forms])
            logger.error(request.POST)
            logger.error(request.FILES)
            messages.error(request, "Erreur à la mise à jour du signalement. ")

            context = {
                'feature': feature,
                'features': Feature.handy.availables(user, project).order_by('updated_on'),
                'feature_types': FeatureType.objects.filter(project=project),
                'feature_type': feature.feature_type,
                'project': project,
                'permissions': Authorization.all_permissions(user, project),
                'feature_form': feature_form,
                'extra_form': extra_form,
                'availables_features': availables_features,
                'linked_formset': linked_formset,
                'attachment_formset': attachment_formset,
                'attachments': attachments,
                'action': 'update',
                'layers': serialized_layers.data,
            }
            return render(request, 'collab/feature/feature_edit.html', context)
        else:

            updated_feature = feature_form.save(
                project=project,
                feature_type=feature_type,
                extra=extra_form.cleaned_data
            )

            # On contextualise l'evenement en fonction des modifications apportés
            data = {}
            data['extra'] = updated_feature.feature_data
            data['feature_title'] = updated_feature.title

            data['feature_status'] = {
                'has_changed': (old_status != updated_feature.status),
                'old_status': old_status,
                'new_status': updated_feature.status,
            }
            data['feature_geom'] = {
                'has_changed': (old_geom != updated_feature.geom),
                'old_geom': old_geom,
                'new_geom': updated_feature.geom.wkt if updated_feature.geom else '',
            }

            Event.objects.create(
                feature_id=updated_feature.feature_id,
                event_type='update',
                object_type='feature',
                user=user,
                project_slug=updated_feature.project.slug,
                feature_type_slug=updated_feature.feature_type.slug,
                data=data
            )

            # Traitement des signalements liés
            for data in linked_formset.cleaned_data:

                feature_link = data.pop('id', None)

                if feature_link:
                    if not data.get('DELETE'):
                        feature_link.relation_type = data.get('relation_type')
                        feature_link.feature_to = data.get('feature_to')
                        feature_link.save()

                    if data.get('DELETE'):
                        feature_link.delete()

                if not feature_link and not data.get('DELETE'):
                    FeatureLink.objects.create(
                        relation_type=data.get('relation_type'),
                        feature_from=feature_id,
                        feature_to=data.get('feature_to')
                    )

            # Traitement des piéces jointes
            for data in attachment_formset.cleaned_data:

                attachment = data.pop('id', None)

                if attachment and data.get('DELETE'):
                    attachment.delete()

                if attachment and not data.get('DELETE'):
                    attachment.attachment_file = data.get('attachment_file')
                    attachment.title = data.get('title')
                    attachment.info = data.get('info')
                    attachment.save()

                if not attachment and not data.get('DELETE'):
                    Attachment.objects.create(
                        attachment_file=data.get('attachment_file'),
                        title=data.get('title'),
                        info=data.get('info'),
                        object_type='feature',
                        project=project,
                        feature_id=feature_id,
                        author=user,
                    )

        return redirect(
            'collab:feature_detail', slug=project.slug,
            feature_type_slug=feature_type.slug, feature_id=feature.feature_id)


class FeatureDelete(DeleteView):
    model = Feature
    pk_url_kwarg = 'feature_id'

    def get_success_url(self):
        feature = self.object
        Event.objects.create(
            feature_id=feature.feature_id,
            event_type='delete',
            object_type='feature',
            user=self.request.user,
            project_slug=feature.project.slug,
            feature_type_slug=feature.feature_type.slug,
            data={
                'extra': feature.feature_data,
                'feature_title': feature.title
            }
        )
        return reverse_lazy(
            'collab:project', kwargs={'slug': feature.project.slug}
        )


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
                        options=data.get("options"),
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
            return render(request, 'collab/feature_type/feature_type_create.html', context)


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
            'structure': structure.data
        }

        return render(request, 'collab/feature_type/feature_type_detail.html', context)


@method_decorator(DECORATORS, name='dispatch')
class ImportFromGeoJSON(SingleObjectMixin, UserPassesTestMixin, View):
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

    def get_feature_data(self, feature_type, properties):

        feature_data = {}
        if hasattr(feature_type, 'customfield_set'):
            for field in feature_type.customfield_set.all():
                feature_data[field.name] = properties.get(field.name)
        return feature_data

    def create_features(self, request, creator, data, feature_type):
        new_features = data.get('features')
        nb_features = len(new_features)
        for feature in new_features:
            properties = feature.get('properties')
            feature_data = self.get_feature_data(feature_type, properties)

            current = Feature.objects.create(
                title=properties.get('title'),
                description=properties.get('description'),
                status='draft',
                creator=creator,
                project=feature_type.project,
                feature_type=feature_type,
                geom=self.get_geom(feature.get('geometry')),
                feature_data=feature_data,
            )

            simili_features = Feature.objects.filter(
                title=current.title, description=current.description
            ).exclude(feature_id=current.feature_id)

            if simili_features.count() > 0:
                for row in simili_features:
                    FeatureLink.objects.get_or_create(
                        relation_type='doublon',
                        feature_from=current.feature_id,
                        feature_to=row.feature_id
                    )
        if nb_features > 0:
            msg = "{nb} signalement(s) importé(s). ".format(nb=nb_features)
            messages.info(request, msg)

    def check_feature_type_slug(self, request, data, feature_type_slug):
        for feat in data.get('features'):
            if feat.get('properties').get('feature_type', 'N/A') != feature_type_slug:
                messages.error(
                    request,
                    "Le type de signalement {source} ne correspond pas à celui en cours d'import: {dest}. ".format(
                        source=feat.get('properties').get('feature_type'),
                        dest=feature_type_slug
                    ))
                raise IntegrityError

    @transaction.atomic
    def post(self, request, slug, feature_type_slug):
        """
        Import d'un fichier GeoJSON

        Disponibilité de la fonction :
            Fonction disponible pour chaque type de signalement de chaque projet (dans la page descriptive du type de signalements)
            Uniquement pour les utilisateurs qui peuvent créer des signalements (contributeurs et niveaux de droits supérieurs du projet)
        Action de la fonction :
            Créer de nouveaux signalements
            La fonction n'est pas capable de mettre à jour des signalements existants ni de supprimer des signalements existants
            Les enregistrements soupçonnés de former des doublons sont marqués automatiquement à l'aide du mécanisme de relation entre signalements. Les doublons sont identifiés par l'égalité de leur titre et de leur description)
            Les enregistrements importés sont enregistrés avec le statut "brouillon"
        Structuration des données importées :
            Le modèle de données supporté par la fonction d'import doit être décrit dans la page descriptive du type de signalements
            Seuls les champs portant les mêmes noms que la table des signalements en base seront exploités
            Pour les champs correspondant à des listes de choix : seules les valeurs seront exploitées (pas les libellés en langage naturel)
            Géométries supportées pour Excel : colonne geom en WKT dans le système de coordonnées attendu (pas de reprojection - cf. DB_SRID dans settings.py)

        En cas d'erreur lors de l'exécution de l'import un compte rendu des erreurs rencontrées doit être présenté à l'utilisateur.
        Si des signalements ont été créés, le nombre de signalements créés doit être indiqué à l'utilisateur.
        """
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
                messages.error(request, "Erreur à lors de l'ajout des signalements. ")

        return redirect('collab:feature_type_detail', slug=slug, feature_type_slug=feature_type_slug)


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


#################
# PROJECT VIEWS #
#################

@method_decorator(DECORATORS[0], name='dispatch')
class ProjectDetail(DetailView):

    model = Project

    # TODO@cbenhabib: renommer en project_detail.html
    template_name = "collab/project/project_home.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        project = self.get_object()
        user = self.request.user

        permissions = Authorization.all_permissions(user, project)

        last_comments = Comment.objects.filter(
            project=project
        ).order_by('-created_on')[0:5]

        serialized_comments = CommentSerializer(last_comments, many=True).data

        features = Feature.objects.filter(
            project=project
        ).order_by('-created_on')

        serilized_projects = ProjectDetailedSerializer(project).data

        context['project'] = serilized_projects
        context['user'] = user
        context['last_comments'] = serialized_comments
        context['last_features'] = features[0:5]
        context['features'] = features
        context['permissions'] = permissions
        context['feature_types'] = project.featuretype_set.all()
        context['is_suscriber'] = Subscription.is_suscriber(user, project)

        # EDC
        layers = Layer.objects.filter(project=project)
        serialized_layers = LayerSerializer(layers, many=True)
        context['layers'] = serialized_layers.data

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
            'project': project,
            'permissions': Authorization.all_permissions(request.user, project),
            'feature_types': project.featuretype_set.all(),
            'is_suscriber': Subscription.is_suscriber(request.user, project),
            'action': 'update'
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
        form.instance.creator = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'create'
        return context


@method_decorator(DECORATORS, name='dispatch')
class ProjectMapping(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = Project.objects.all()

    LayerFormSet = modelformset_factory(
        Layer,
        can_delete=True,
        form=LayerForm,
        extra=0,
        fields=('title', 'service', 'order', 'schema_type', 'options')
    )

    def test_func(self):
        user = self.request.user
        project = self.get_object()
        return Authorization.has_permission(user, 'can_update_project', project)

    def get(self, request, slug):

        project = self.get_object()
        layers = Layer.objects.filter(project=project)
        serialized_layers = LayerSerializer(layers, many=True)
        layer_formset = self.LayerFormSet(queryset=layers)

        context = {
            'project': project,
            'layers': serialized_layers.data,
            'layer_formset': layer_formset
        }
        return render(request, 'collab/project/project_mapping.html', context)

    def post(self, request, slug):
        project = self.get_object()
        layers = Layer.objects.filter(project=project)
        serialized_layers = LayerSerializer(layers, many=True)
        layer_formset = self.LayerFormSet(request.POST or None)
        if layer_formset.is_valid():

            for data in layer_formset.cleaned_data:
                # id contient l'instance si existante
                layer = data.pop("id", None)
                is_deleted = data.pop("DELETE", False)
                if layer:
                    if is_deleted:
                        layer.delete()
                    else:
                        for attr, value in data.items():
                            setattr(layer, attr, value)
                        layer.save()

                elif not layer and not is_deleted:
                    data['project'] = project
                    Layer.objects.create(**data)

                # TODO @cbenhabib: afin d'avoir une valeur unique d'ordre.
                layers = Layer.objects.filter(project=project).order_by('order')
                for idx, layer in enumerate(layers):
                    layer.order = idx
                    layer.save(update_fields=['order'])
                layer_formset = self.LayerFormSet(queryset=layers)
        else:
            logger.error(layer_formset.errors)

        context = {
            'project': project,
            'layers': serialized_layers.data,
            'layer_formset': layer_formset
        }
        return render(request, 'collab/project/project_mapping.html', context)

        messages.error(request, "L'édition des couches cartographiques a échouée. ")
        logger.error(layer_formset.errors)
        context = {
            'project': project,
            'layers': layers,
            'layer_formset': layer_formset
        }
        return render(request, 'collab/project/project_mapping.html', context)


@method_decorator(DECORATORS, name='dispatch')
class ProjectMembers(SingleObjectMixin, UserPassesTestMixin, View):
    queryset = Project.objects.all()
    AuthorizationFormSet = modelformset_factory(
        Authorization,
        can_delete=True,
        form=AuthorizationForm,
        formset=AuthorizationBaseFS,
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
        formset = self.AuthorizationFormSet(
            queryset=Authorization.objects.filter(
                project=project, user__is_active=True))
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

        return render(request, 'collab/project/project_members.html', context)

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

            return redirect('collab:project_members', slug=slug)

        context = {
            "title": "Gestion des membres du projet {}".format(project.title),
            'authorised': authorised,
            'permissions': permissions,
            'project': project,
            'formset': formset,
            'feature_types': FeatureType.objects.filter(project=project)
        }
        return render(request, 'collab/project/project_members.html', context)


######################
# SUBSCRIPTION VIEWS #
######################

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

        return redirect('collab:project', slug=slug)
