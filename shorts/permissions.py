from rest_framework.permissions import BasePermission

class IsAdminOrIsUserMatch(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.user.is_admin or request.user.is_superuser or obj.uploader == request.user