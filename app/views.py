from .choices import Status
from rest_framework import viewsets
from .models import Order, OrderLog
from .serializers import OrderSimpleSerializer, OrderDetailSerializer
from .permissions import AllowOnlyForAdminOwnerOrExecutor, UpdateOnlyAdminOrExecutor
from rest_framework.permissions import IsAuthenticated
from users.choices import UserRole
from django.db.models import Case, When, Value, Q, Count, DateField, DurationField, F, Subquery, OuterRef
from django.db.models.functions import Now, TruncDate
from django.db.models.expressions import Subquery
from django.contrib.auth.models import User




class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, AllowOnlyForAdminOwnerOrExecutor, UpdateOnlyAdminOrExecutor,)

    def get_serializer_class(self):
        return OrderSimpleSerializer if self.action == 'list' else OrderDetailSerializer

    def get_queryset(self):
        queryset = Order.objects.all()
        if hasattr(self.request.user, 'profile'):
            if self.request.user.profile.role == UserRole.CLIENT:
                return queryset.filter(owner=self.request.user)
            elif self.request.user.profile.role == UserRole.PLANNER:
                return queryset.filter(status=Status.PAYMENT_AWAIT)
            elif self.request.user.profile.role == UserRole.EXECUTOR:
                queryset = queryset.filter(executor=self.request.user)

        """
        For admins, executors and management -> sorted orders.
        List of orders must be presented most practic way for executor (and admin for control).
        This is why it gonna not printing finished orders, the first orders will be those waiting for a payment and then
        orders with stage and whose deadlines are coming.
        Stage does not matter while sorting by deadlines, because more important is execute order
        before deadline expired than execute older orders.
        """
        return queryset.exclude(status__in=['5', '6']).annotate(
            #select first orders with state as 'Await_for_payment_date'
            await_for_payment_first=Case(
                When(status='4', then=Value(0)),
                default=Value(1)
            ),
            #select first orders that stage was set
            with_stage_first=Case(
                When(stage__isnull=False, then=Value(0)),
                default=Value(1)
            ),
            #getting suitable num of Event base on stage
            #query gotta find appropriate OrderLog dependent to stage because has to get deadline from this row
            lookup_event=Case(
                When(stage='1', then=Value('9')),
                When(stage='2', then=Value('10')),
                When(stage='3', then=Value('11')),
                When(stage='4', then=Value('12')),
                default=Value(None),
            ),
            #retrieve appropriate row and deadline from it
            deadline=Subquery(
                OrderLog.objects.filter(
                    order=OuterRef('pk'),
                    event=OuterRef('lookup_event')
                ).values('deadline'),
                output_field=DateField()
            ),
            #calculate diff between today and deadline (if exists, else None)
            time_left=Case(
                When(deadline__isnull=False, then=F('deadline') - TruncDate(Now())),
                default=Value(None),
                output_field=DurationField()
            )
        ).order_by(
            'await_for_payment_first',
            'with_stage_first',
            'time_left'
        )


    """
    After save a object is necessery to assign it to executor with
    the least number of current executing_orders 
    (executing_orders that status is not 5 and 6)
    """
    def perform_create(self, serializer):
        #executor - user with the least number of orders
        executor = User.objects.filter(
            profile__role='2'
        ).annotate(
            num_of_active_executing_orders=Count(
                'executing_orders', 
                filter=Q(executing_orders__status__in=['1', '2', '3', '4'])
            )
        ).order_by(
            'num_of_active_executing_orders'
        ).first()
        #save object
        return serializer.save(
            owner=self.request.user,
            executor=executor
        )


