from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import F
from django.forms import modelformset_factory
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import DeleteView

from api.serializers import EventSerializer
from api.serializers import FeatureLinkSerializer
from geocontrib import logger
from geocontrib.forms import AttachmentForm
from geocontrib.forms import CommentForm
from geocontrib.forms import FeatureBaseForm
from geocontrib.forms import FeatureExtraForm
from geocontrib.forms import FeatureLinkForm
from geocontrib.models import Attachment
from geocontrib.models import Authorization
from geocontrib.models import CustomField
from geocontrib.models import Event
from geocontrib.models import Feature
from geocontrib.models import FeatureLink
from geocontrib.models import FeatureType
from geocontrib.models import Project
from geocontrib.views.common import BaseMapContextMixin
from geocontrib.views.common import DECORATORS


@method_decorator(DECORATORS, name='dispatch')
class FeatureCreate(BaseMapContextMixin, UserPassesTestMixin, View):

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
        permissions = Authorization.all_permissions(user, project)

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

        context = {**self.get_context_data(), **{
            'features': Feature.handy.availables(user, project).order_by('updated_on'),
            'feature_type': feature_type,
            'project': project,
            'permissions': permissions,
            'feature_form': feature_form,
            'extra_form': extra_form,
            'linked_formset': linked_formset,
            'attachment_formset': attachment_formset,
            'action': 'create',
        }}
        return render(request, 'geocontrib/feature/feature_edit.html', context)

    def post(self, request, slug, feature_type_slug):

        user = request.user
        feature_type = self.get_object()
        project = feature_type.project
        permissions = Authorization.all_permissions(user, project)

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
                            feature_from=feature,
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
                    'geocontrib:feature_detail', slug=project.slug,
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

        context = {**self.get_context_data(), **{
            'features': Feature.handy.availables(user, project).order_by('updated_on'),
            'feature_type': feature_type,
            'project': project,
            'permissions': permissions,
            'feature_form': feature_form,
            'extra_form': extra_form,
            'linked_formset': linked_formset,
            'attachment_formset': attachment_formset,
            'action': 'create',
        }}
        return render(request, 'geocontrib/feature/feature_edit.html', context)


@method_decorator(DECORATORS[0], name='dispatch')
class FeatureList(BaseMapContextMixin, UserPassesTestMixin, View):
    queryset = Project.objects.all()

    def test_func(self):
        user = self.request.user
        project = self.get_object()
        return Authorization.has_permission(user, 'can_view_feature', project)

    def get(self, request, slug, *args, **kwargs):
        project = self.get_object()

        user = request.user

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
        context = self.get_context_data()
        context['features'] = features
        context['feature_types'] = feature_types
        context['project'] = project
        context['permissions'] = permissions
        context['status_choices'] = Feature.STATUS_CHOICES
        return render(request, 'geocontrib/feature/feature_list.html', context)


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


@method_decorator(DECORATORS, name='dispatch')
class FeatureUpdate(BaseMapContextMixin, UserPassesTestMixin, View):

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

        context = {**self.get_context_data(), **{
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
        }}
        return render(request, 'geocontrib/feature/feature_edit.html', context)

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

        extra = CustomField.objects.filter(feature_type=feature_type)

        feature_form = FeatureBaseForm(
            request.POST, instance=feature, feature_type=feature_type, user=user)

        extra_form = FeatureExtraForm(request.POST, feature=feature, extra=extra)

        linked_formset = self.LinkedFormset(
            request.POST,
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

            context = {**self.get_context_data(), **{
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
            }}
            return render(request, 'geocontrib/feature/feature_edit.html', context)
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
                        feature_from=updated_feature,
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
            'geocontrib:feature_detail', slug=project.slug,
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
            'geocontrib:project', kwargs={'slug': feature.project.slug}
        )
