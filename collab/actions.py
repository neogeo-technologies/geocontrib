from collab.views.services.feature_services import delete_feature_table
from collab.views.services.project_services import project_features_types
from django.db import models

from django.shortcuts import get_object_or_404
APP_NAME = __package__.split('.')[0]


def delete_project(modeladmin, request, queryset):
    """
        delete project and associated features tables
    """
    for project in queryset:

        # remove all project tables
        feature_slug_list = project_features_types(APP_NAME, project.slug)
        for feature_type_slug in feature_slug_list:
            deletion = delete_feature_table(APP_NAME, project.slug, feature_type_slug)
        message = "le(s) projet(s) a/ont été supprimé "
        modeladmin.message_user(request, "%s." % message)
        # remove the project
        project.delete()
delete_project.short_description = """Supprimer le(s) projet(s) et les tables des signalements"""
