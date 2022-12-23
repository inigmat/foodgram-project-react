from rest_framework import permissions


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, _view, obj):
        if request.user.is_authenticated and (
                request.user.is_admin or obj.author
                == request.user or request.method == 'POST'):
            return True
        return request.method in permissions.SAFE_METHODS


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, _view):
        return (
            request.method in ('GET',)
            or request.user.is_authenticated
            and request.user.is_admin
        )
