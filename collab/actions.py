from collab.views.services.feature_services import delete_feature_table
from collab.views.services.project_services import project_features_types
from collab import models

APP_NAME = __package__.split('.')[0]


def delete_project(modeladmin, request, queryset):
    """
        delete project and associated features tables
    """
    for elt in queryset:
        # remove the project
        project = models.Project.objects.get(slug=elt.slug)
        project.delete()
        # remove all project tables
        feature_slug_list = project_features_types(APP_NAME, elt.slug)
        for feature_type_slug in feature_slug_list:
            try:
                deletion = delete_feature_table(APP_NAME, elt.slug, feature_type_slug)
            except Exception as e:
                print(deletion)
                pass

        message = "le(s) projet(s) a/ont été supprimé "
        modeladmin.message_user(request, "%s." % message)

delete_project.short_description = """Supprimer le(s) projet(s) et les tables des signalements"""
