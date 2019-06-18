from collab import models
from collab.views.project_services import get_feature_detail
from django.http import JsonResponse
# from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

APP_NAME = __package__.split('.')[0]


@method_decorator([csrf_exempt], name='dispatch')
class ProjectAttachment(View):

    def post(self, request, project_slug, feature_type_slug, feature_id):
        """
            Add feature attachment
            @param
            @return JSON
        """
        # update forms fields
        form_data = request.POST.dict()
        project, feature, utilisateur = get_feature_detail(
            APP_NAME, project_slug, feature_type_slug, feature_id)
        # create comment
        obj = models.Attachment.objects.create(author=request.user,
                                               feature_id=feature['feature_id'],
                                               title=form_data.get('title', ''),
                                               type_objet='0',
                                               info=form_data.get('info', ''),
                                               project=project,
                                               file=request.FILES.get('file', ''))
        # Ajout d'une piece jointe
        models.Event.objects.create(
            user=request.user,
            event_type='create_attachment',
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
        # return redirect('project_feature_detail', project_slug=project_slug,
        #                 feature_type_slug=feature_type_slug, feature_id=feature_id)
