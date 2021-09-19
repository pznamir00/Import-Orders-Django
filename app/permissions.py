from rest_framework.permissions import BasePermission
from .models import Comment
from django.db.models import Q
from users.choices import UserRole
from .choices import Status



class DenyForOtherClientsAndExecutors(BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        Object is available for admins, planners, management, owner and assigned executor
        An access is denied for other clients and executors
        """
        if request.user.is_superuser:
            return True
        if request.user.profile.role == UserRole.CLIENT and obj.owner != request.user:
            return False
        if request.user.profile.role == UserRole.EXECUTOR and obj.executor != request.user:
            return False
        return True



class AllowCommentsOnlyForAdminOwnerOrExecutorOfOrder(BasePermission):
    """
    Check if user has access to order (as above but by 'parent_lookup_orders' field)
    """
    def has_permission(self, request, view):
        order_pk = request.kwargs['parent_lookup_orders']
        return request.user.is_superuser or Comment.objects.filter(order=order_pk).exists()



class DeleteOrUpdateOnlyForOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_superuser



class UpdateBasedOnRole(BasePermission):
    update_methods = ('PUT', 'PATCH',)
    """
    Different users have an access to update dependent on status
    """
    def has_object_permission(self, request, view, obj):
        if request.method in self.update_methods:
            if request.user.is_superuser:
                return True
            if obj.status == Status.APPROVAL_AWAIT and request.user.profile.role == UserRole.MANAGEMENT:
                return True
            if obj.status == Status.PAYMENT_AWAIT and request.user.profile.role == UserRole.PLANNER:
                return True
            return obj.status in [Status.NEW, Status.PROCESSING] and request.user.profile.role == UserRole.EXECUTOR
        return True




