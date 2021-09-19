from rest_framework import serializers
from .models import Order, Log, Comment
from .choices import Status, Stage, Event
from .helpers import create_log





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
        extra_kwargs = {
            'title': { 'required': False },
            'content': { 'required': False }
        }





class OrderPlannerUpdateSerializer(serializers.ModelSerializer):
    payment_date = serializers.DateField(write_only=True)
    
    class Meta:
        model = Order
        fields = ('payment_date',)

    def validate(self, data):
        if 'payment_date' not in data:
            raise serializers.ValidationError({ 'payment_date': 'This field is required' })
        return data

    def update(self, instance, validated_data):
        #set payment date
        payment_date = validated_data.pop('payment_date')
        create_log(instance, Event.PAYMENT_DATE_WAS_SET, payment_date)
        instance.status = 2
        instance.save()
        return instance





class OrderManagementUpdateSerializer(serializers.ModelSerializer):
    agreement = serializers.BooleanField(write_only=True)
    
    class Meta:
        model = Order
        fields = ('agreement',)

    def validate(self, data):
        if 'agreement' not in data:
            raise serializers.ValidationError({ 'agreement': 'This field is required' })
        return data

    def update(self, instance, validated_data):
        agreement = validated_data.pop('agreement')
        create_log(instance, Event.ACCEPTED_BY_BOARD if agreement else Event.REJECTED)
        new_status = 2 if agreement else 5
        instance.status = new_status
        instance.save()
        return instance





class OrderExecutorUpdateSerializer(serializers.ModelSerializer):
    deadline = serializers.DateField(required=False)

    class Meta:
        model = Order
        fields = ('status', 'stage', 'priority', 'origin', 'deadline',)

    def validate(self, data):
        instance = self.instance
        #check the status
        if 'status' in data:
            if instance.status == Status.NEW:
                if 'deadline' not in data:
                    raise serializers.ValidationError({
                        'status': 'For update field status to \'Processing\' you must pass deadline parameter for set stage automatically'
                    })                  
                if data['status'] != Status.PROCESSING:
                    raise serializers.ValidationError({
                        'status': 'Wrong value. You must pass 2 for this status'
                    })
            elif instance.status == Status.PROCESSING and data['status'] not in [Status.PAYMENT_AWAIT, Status.APPROVAL_AWAIT, Status.FINISHED]:
                raise serializers.ValidationError({
                    'status': 'Wrong value. You must pass 3, 4 or 6 for this status'
                })
        #check the stage
        if 'stage' in data:
            if 'deadline' not in data:
                raise serializers.ValidationError({
                    'stage': 'If you want to change stage, you must pass a deadline parameter for new stage'
                })
            try:
                if int(instance.stage) + 1 != int(data['stage']):
                    raise serializers.ValidationError({
                        'stage': 'Wrong value. You must pass value ' + str(int(instance.stage) + 1) + ' for this stage'
                    })
            except TypeError as e:
                raise serializers.ValidationError({
                    'stage': 'You can\'t pass stage before status is \'Processing\' ' + str(e)
                })
        return data
        
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
            stage_event = { '1': '9', '2': '10', '3': '11', '4': '12', '5': '13' }
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
