from collab import models
from collab.views.project_services import get_feature_detail
from django.http import JsonResponse
from django.views import View

APP_NAME = __package__.split('.')[0]


class ProjectComment(View):

    def post(self, request, project_slug, feature_type_slug, feature_id):
        """
            Add feature comment
            @param
            @return JSON
        """
        comment = request.POST.get('comment', '')
        project, feature, user = get_feature_detail(APP_NAME, project_slug,
                                                    feature_type_slug, feature_id)
        # create comment
        comment_obj = models.Comment.objects.create(author=request.user,
                                            feature_id=feature['feature_id'],
                                            feature_type_slug=feature_type_slug,
                                            comment=comment,
                                            project=project)
        models.Event.objects.create(
            user=request.user,
            event_type='create',
            object_type='comment',
            project_slug=project.slug,
            feature_id=feature['feature_id'],
            comment_id=comment_obj.comment_id,
            feature_type_slug=feature_type_slug,
            data={}
        )

        # create attachement
        if request.FILES.get('file', ''):
            form_data = request.POST.dict()
            project, feature, utilisateur = get_feature_detail(APP_NAME, project_slug,
                                                               feature_type_slug, feature_id)
            # create attachment
            form_data = request.POST.dict()
            obj = models.Attachment.objects.create(author=request.user,
                                                   title=form_data.get('title', ''),
                                                   type_objet='1',
                                                   comment=comment_obj,
                                                   info=form_data.get('info', ''),
                                                   project=project,
                                                   file=request.FILES.get('file', ''))
            # Ajout d'une piece jointe
            models.Event.objects.create(
                user=request.user,
                event_type='create',
                object_type='attachment',
                project_slug=project.slug,
                feature_id=feature['feature_id'],
                attachment_id=obj.attachment_id,
                feature_type_slug=feature_type_slug,
                data={}
            )

        context = {'project_slug': project_slug,
                   'feature_type_slug': feature_type_slug, 'feature_id': feature_id}
        return JsonResponse(context)
