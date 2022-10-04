from rest_framework import permissions

from geocontrib.models import Authorization


class ProjectPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return Authorization.has_permission(request.user, 'can_update_project', obj)
