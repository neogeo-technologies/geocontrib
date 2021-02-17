from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.detail import SingleObjectMixin

from api.serializers import EventSerializer
from api.serializers import FeatureLinkSerializer
from geocontrib import logger
from geocontrib.forms import AttachmentForm
from geocontrib.forms import CommentForm
from geocontrib.models import Attachment
from geocontrib.models import Authorization
from geocontrib.models import Comment
from geocontrib.models import Event
from geocontrib.models import Feature
from geocontrib.models import FeatureLink
from geocontrib.models import FeatureType
from geocontrib.views.common import BaseMapContextMixin
from geocontrib.views.common import DECORATORS


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
            'geocontrib:feature_update', slug=slug,
            feature_type_slug=feature_type_slug, feature_id=feature_id)


@method_decorator(DECORATORS, name='dispatch')
class CommentCreate(BaseMapContextMixin, UserPassesTestMixin, View):
    queryset = Feature.objects.all()
    pk_url_kwarg = 'feature_id'

    def test_func(self):
        user = self.request.user
        feature = self.get_object()
        project = feature.project
        return Authorization.has_permission(user, 'can_create_feature', project)

    def get(self, request, slug, feature_type_slug, feature_id):
        return redirect(
            'geocontrib:feature_detail',
            slug=slug,
            feature_type_slug=feature_type_slug,
            feature_id=feature_id)

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
                'geocontrib:feature_detail',
                slug=slug,
                feature_type_slug=feature_type_slug,
                feature_id=feature_id)
        else:
            logger.error(form.errors)

        events = Event.objects.filter(feature_id=feature.feature_id).order_by('created_on')
        serialized_events = EventSerializer(events, many=True)

        context = {**self.get_context_data(), **{
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
            'comment_form': form,
        }}

        return render(request, 'geocontrib/feature/feature_detail.html', context)
