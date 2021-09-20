from .choices import Status, Event, Origin, Priority
from rest_framework import viewsets, generics
from rest_framework.response import Response
from .models import Order, Log, Comment
from .serializers import *
from .permissions import *
from rest_framework.permissions import IsAuthenticated
from users.choices import UserRole
from django.db.models import Case, When, Value, Q, Count, DateField, DurationField, F, Subquery, OuterRef
from django.db.models.functions import Now, TruncDate
from django.db.models.expressions import Subquery
from django.contrib.auth.models import User
from .helpers import create_log





class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = (
        IsAuthenticated, 
        PutMethodNotAllowed,
        DenyForOtherClientsAndExecutors, 
        UpdateBasedOnRole,
    )

    def get_serializer_class(self):
        if self.request.method in UpdateBasedOnRole.update_methods:
            if hasattr(self.request.user, 'profile'):
                if self.request.user.profile.role == UserRole.PLANNER:
                    return OrderPlannerUpdateSerializer
                if self.request.user.profile.role == UserRole.MANAGEMENT:
                    return OrderManagementUpdateSerializer
                if self.request.user.profile.role == UserRole.EXECUTOR:
                    return OrderExecutorUpdateSerializer
        return OrderSimpleSerializer if self.action == 'list' else OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.all()
        """
        Admin has no profile 
        his role is recognizable by is_superuser property and this is not necessery.
        This is why app has to check if profile prop exists
        """
        if hasattr(self.request.user, 'profile'):
            if self.request.user.profile.role == UserRole.CLIENT:
                #client receives only own orders
                return queryset.filter(owner=self.request.user)
            elif self.request.user.profile.role == UserRole.PLANNER:
                #planner receives only orders with status=PAYMENT_AWAIT
                return queryset.filter(status=Status.PAYMENT_AWAIT)
            elif self.request.user.profile.role == UserRole.MANAGEMENT:
                #managers receives only orders with status=APPROVAL_AWAIT
                return queryset.filter(status=Status.APPROVAL_AWAIT)
            elif self.request.user.profile.role == UserRole.EXECUTOR:
                #executor receives only orders that executes
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
                When(status=4, then=Value(0)),
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
                Log.objects.filter(
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
            'time_left',
            '-priority'
        )
        
    def perform_create(self, serializer):
        """
        After save a object is necessery to assign it to executor with
        the least number of current executing_orders 
        (executing_orders that status is not 5 and 6)
        """
        executor = User.objects.filter(
            profile__role='2'
        ).annotate(
            num_of_active_executing_orders=Count(
                'executing_orders', 
                filter=(~Q(executing_orders__status__in=['5', '6']))
            )
        ).order_by(
            'num_of_active_executing_orders'
        ).first()
        #save object
        obj = serializer.save(
            owner=self.request.user,
            executor=executor
        )
        #set log
        create_log(obj, Event.CREATED)
        return obj





class OrderCommentViewSet(viewsets.ModelViewSet):
    serializer_class = OrderCommentSerializer
    permissions_classes = (
        IsAuthenticated, 
        AllowCommentsOnlyForAdminOwnerOrExecutorOfOrder,
        DeleteOrUpdateOnlyForOwnerOrAdmin,
    )

    def get_queryset(self):
        order_pk = self.kwargs['parent_lookup_order']
        return Comment.objects.filter(order=order_pk)





class StatusView(generics.RetrieveAPIView):
    def get(self, request):
        return Response(Status.choices)





class PriorityView(generics.RetrieveAPIView):
    def get(self, request):
        return Response(Priority.choices)





class StageView(generics.RetrieveAPIView):
    def get(self, request):
        return Response(Stage.choices)





class OriginView(generics.RetrieveAPIView):
    def get(self, request):
        return Response(Origin.choices)