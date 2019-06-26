from collab import models
from collab.views.services.feature_services import get_feature_detail
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

APP_NAME = __package__.split('.')[0]


@method_decorator([csrf_exempt], name='dispatch')
class Attachment(View):

    def post(self, request, project_slug, feature_type_slug, feature_id):
        """
            Add/ delete feature attachment
            @param
            @return JSON
        """
        # import pdb; pdb.set_trace()
        # update forms fields
        form_data = request.POST.dict()
        project, feature, utilisateur = get_feature_detail(
            APP_NAME, project_slug, feature_type_slug, feature_id)

        if request.POST.dict().get('_method', '') == 'delete':
            try:
                attachment_obj = models.Attachment.objects.get(
                                 attachment_id=request.POST.dict().get('attachment_id', ''))
                attachment_obj.delete()
                return redirect('project_feature_detail', project_slug=project_slug,
                                 feature_type_slug=feature_type_slug, feature_id=feature_id)
            except Exception as e:
                msg = "Une erreur s'est produite, la pièce jointe n'a pas pu être supprimée"
                # logger = logging.getLogger(__name__)
                # logger.exception(deletion)
                request.session['error'] = msg
                return redirect('project_feature_detail', project_slug=project_slug,
                                feature_type_slug=feature_type_slug, feature_id=feature_id)
        else:
            # create comment
            obj = models.Attachment.objects.create(author=request.user,
                                                   feature_id=feature['feature_id'],
                                                   feature_type_slug=feature_type_slug,
                                                   title=form_data.get('title', ''),
                                                   type_objet='0',
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
            # return redirect('project_feature_detail', project_slug=project_slug,
            #                 feature_type_slug=feature_type_slug, feature_id=feature_id)
