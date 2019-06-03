from collab import models
from collab.views.project_services import get_feature_detail
from django.shortcuts import redirect
from django.views import View

APP_NAME = __package__.split('.')[0]


class ProjectAttachment(View):

    def post(self, request, project_slug, feature_type, feature_pk):
        """
            Add feature attachment
            @param
            @return JSON
        """
        # update forms fields
        form_data = request.POST.dict()
        project, feature, utilisateur = get_feature_detail(APP_NAME, project_slug,
                                                          feature_type, feature_pk)
        # create comment
        obj = models.Attachment.objects.create(author=request.user,
                                               feature_id=feature['feature_id'],
                                               title=form_data.get('title', ''),
                                               type_objet='0',
                                               info=form_data.get('info', ''),
                                               project=project,
                                               file=request.FILES.get('file', ''))
        return redirect('project_feature_detail', project_slug=project_slug,
                        feature_type=feature_type, feature_pk=feature_pk)
