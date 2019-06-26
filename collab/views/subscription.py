from collab import models
from collab.views.services.feature_services import get_feature_detail
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

APP_NAME = __package__.split('.')[0]


@method_decorator([csrf_exempt], name='dispatch')
class Subscription(View):

    def post(self, request, project_slug, feature_type_slug, feature_id):
        """
            Add Subscription
            @param
            @return JSON
        """
        # update forms fields
        form_data = request.POST.dict()
        if 'subscribe' in form_data:
            obj, _created = models.Subscription.objects.get_or_create(feature_id=feature_id,
                                                            project_slug=project_slug)
            # Add user
            if request.user:
                obj.users.add(request.user)
                obj.save()
        else:
            try:
                obj = models.Subscription.objects.get(feature_id=feature_id,
                                                      project_slug=project_slug)
                # remove user
                if request.user:
                    obj.users.remove(request.user)
                    obj.save()
            except Exception as e:
                pass

        return redirect('project_feature_detail', project_slug=project_slug,
                        feature_type_slug=feature_type_slug, feature_id=feature_id)
