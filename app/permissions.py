from rest_framework.permissions import BasePermission



class AllowOnlyForAdminOwnerOrExecutor(BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        An access to data can get only people associated with order.
        That are admin, owner (who created) and executor
        """
        return (obj.owner == request.user or obj.executor == request.user) or request.user.is_superuser



class UpdateOnlyAdminOrExecutor(BasePermission):
    update_methods = ('PUT', 'PATCH',)
    """
    Update is allowed only for executor (for changing a status etc.)
    Admin of course has such option also
    """
    def has_object_permission(self, request, view, obj):
        if request.method in self.update_methods:
            return obj.executor == request.user or request.user.is_superuser
        return True


