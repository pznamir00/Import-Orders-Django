from backend.app.choices import Status
from rest_framework import viewsets
from .models import Order
from .serializers import OrderSimpleSerializer, OrderDetailSerializer
from .permissions import AllowOnlyForAdminOwnerOrExecutor, UpdateOnlyAdminOrExecutor
from rest_framework.permissions import IsAuthenticated
from users.choices import UserRole
from django.db.models import Case, When, Value, Q, Count
from datetime import date
from django.contrib.auth.models import User




class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, AllowOnlyForAdminOwnerOrExecutor, UpdateOnlyAdminOrExecutor,)

    def get_serializer_class(self):
        return OrderSimpleSerializer if self.action == 'list' else OrderDetailSerializer

    def get_queryset(self):
        queryset = Order.objects.all()
        if self.request.user.profile:
            if self.request.user.profile.role == UserRole.CLIENT:
                return queryset.filter(owner=self.request.user)
            elif self.request.user.profile.role == UserRole.PLANNER:
                return queryset.filter(status=Status.PAYMENT_AWAIT)
            elif self.request.user.profile.role == UserRole.EXECUTOR:
                queryset = queryset.filter(executor=self.request.user)
        """
        for admins, executors and management -> sorted orders
        """
        return queryset.exclude(status__in=['5', '6']).annotate(
            await_for_payment_first=Case(
                When(status='4', then=Value(0)),
                default=Value(1)
            ),
            deadline=Case(
                When(stage='1', then=Value(Q(logs__event='9').values_list('additional_info'))),
                When(stage='2', then=Value(Q(logs__event='10').values_list('additional_info'))),
                When(stage='3', then=Value(Q(logs__event='11').values_list('additional_info'))),
                When(stage='4', then=Value(Q(logs__event='12').values_list('additional_info'))),
                When(stage='5', then=Value(Q(logs__event='13').values_list('additional_info')))
            ),
            dates_diff=Value('deadline', date.today())
        ).order_by(
            'await_for_payment_first'
        ).order_by(
            'dates_diff'
        )

    def perform_create(self, serializer):
        executor = User.objects.filter(
            profile__role='2'
        ).annotate(
            num_of_orders=Count('orders')
        ).order_by(
            'num_of_orders'
        ).first()
        return serializer.save(
            owner=self.request.user,
            executor=executor
        )


