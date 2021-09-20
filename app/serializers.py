from rest_framework import serializers
from .models import Order, Log, Comment
from .choices import Status, Stage, Event
from .helpers import create_log
from .validators import CheckStageValidator, CheckStatusValidator





class OrderLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ('event', 'recorded_time', 'deadline',)





class OrderCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'





class OrderSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('pk', 'title', 'status', 'executor',)





class OrderSerializer(serializers.ModelSerializer):
    logs = OrderLogSerializer(many=True, read_only=True)
    comments = OrderCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('owner',)





class OrderPlannerUpdateSerializer(serializers.Serializer):
    payment_date = serializers.DateField(write_only=True, required=True)

    def update(self, instance, validated_data):
        #set payment date
        payment_date = validated_data.pop('payment_date')
        create_log(instance, Event.PAYMENT_DATE_WAS_SET, payment_date)
        instance.status = 2
        instance.save()
        return instance





class OrderManagementUpdateSerializer(serializers.Serializer):
    agreement = serializers.BooleanField(write_only=True, required=True)

    def update(self, instance, validated_data):
        agreement = validated_data.pop('agreement')
        create_log(instance, Event.ACCEPTED_BY_BOARD if agreement else Event.REJECTED)
        new_status = Status.PROCESSING if agreement else Status.REJECTED
        instance.status = new_status
        instance.save()
        return instance





class OrderExecutorUpdateSerializer(serializers.ModelSerializer):
    deadline = serializers.DateField(required=False)

    class Meta:
        model = Order
        fields = ('status', 'stage', 'priority', 'origin', 'deadline',)
        validators = [
            CheckStageValidator(), 
            CheckStatusValidator()
        ]
        
    def update(self, instance, validated_data):
        if 'status' in validated_data:
            """
            If user attempts assign new value for status, it is necessery to
            generate new log with this information.
            Additional:
                for getting to Status.PROCESSING first time 
                app has to assign default Stage for object
            """
            if instance.status == Status.NEW and validated_data['status'] == Status.PROCESSING:
                #set default stage on 'In planning'
                validated_data['stage'] = Stage.PLAN
                create_log(instance, Event.STARTED)
            if instance.status == Status.PROCESSING and validated_data['status'] == Status.PAYMENT_AWAIT:
                create_log(instance, Event.PAYMENT_REQUESTED)
            if instance.status == Status.PROCESSING and validated_data['status'] == Status.APPROVAL_AWAIT:
                create_log(instance, Event.APPROVAL_REQUESTED)
            if validated_data['status'] == Status.FINISHED:
                create_log(instance, Event.FINISHED)
        if 'stage' in validated_data:
            """
            Create logs for stage update.
            stage_event is dict that keys are number of Stages and values are
            matched Events for logs.
            """
            stage_event = { 
                Stage.PLAN: Event.SET_PLAN_END_DATE, 
                Stage.LOG: Event.SET_LOG_END_DATE, 
                Stage.TRANS: Event.SET_TRANS_END_DATE, 
                Stage.DONE: Event.SET_DONE_END_DATE, 
                Stage.COMPL: Event.SET_COMPLAINT_END_DATE 
            }
            create_log(
                instance, 
                stage_event[validated_data['stage']], 
                deadline=validated_data['deadline']
            )
        #update instance based on validated_data dict
        for key in validated_data:
            setattr(instance, key, validated_data[key])
        #save
        instance.save()
        return instance
