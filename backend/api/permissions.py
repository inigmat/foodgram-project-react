from rest_framework import permissions


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, _view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, _view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin
                or obj.author == request.user)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, _view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )
