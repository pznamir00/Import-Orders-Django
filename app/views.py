from rest_framework import viewsets
from .models import Order
from .serializers import OrderSerializer, OrderDetailSerializer
from .permissions import AllowOnlyForAdminOwnerOrExecutor, UpdateOnlyAdminOrExecutor
from rest_framework.permissions import IsAuthenticated
from users.choices import UserRole
from django.db.models import Case, When, Value



class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated, AllowOnlyForAdminOwnerOrExecutor, UpdateOnlyAdminOrExecutor,)

    def get_queryset(self):
        queryset = Order.objects.all()
        if self.request.user.role == UserRole.CLIENT:
            return queryset.filter(owner=self.request.user)
        elif self.request.user.role == UserRole.EXECUTOR:
            queryset = queryset.filter(executor=self.request.user)
        
        queryset = queryset.exclude(status__in=['5', '6']).annotate(
            await_for_payment_first=Case(
                When(status='4', then=Value(1)),
                When(status__in=['1', '2', '3'], then=Value(2))
            ),
            close_to_expire_date=None
        ).order_by('await_for_payment_first').order_by('close_to_expire_date')

        return queryset