from rest_framework.permissions import BasePermission


class CreateOnlyForAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_superuser
        return True