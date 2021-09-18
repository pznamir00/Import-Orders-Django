from .models import OrderComment
from django.db.models import Q
from rest_framework.permissions import BasePermission



class AllowOnlyForAdminOwnerOrExecutor(BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        An access to data can get only people associated with order.
        That are admin, owner (who created) and executor
        """
        return (obj.owner == request.user or obj.executor == request.user) or request.user.is_superuser



class AllowCommentsOnlyForAdminOwnerOrExecutorOfOrder(BasePermission):
    def has_permission(self, request, view):
        """
        Check if user has access to order (as above but by 'parent_lookup_orders' field)
        """
        order_pk = request.kwargs['parent_lookup_orders']
        return request.user.is_superuser or OrderComment.objects.filter(
            Q(order__owner=order_pk) | Q(order__executor=order_pk)
        ).exists()



class DeleteOrUpdateOnlyForOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_superuser



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




