from rest_framework import permissions


class RecipePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ("list", "retrieve"):
            return True
        elif view.action == "create":
            return request.user.is_authenticated
        elif view.action in ("partial_update", "destroy"):
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if view.action in ("partial_update", "destroy"):
            return obj.author == request.user
        return True
