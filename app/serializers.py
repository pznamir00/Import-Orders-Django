from rest_framework import serializers
from .models import Order, Log, Comment
from .choices import Status, Stage





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
            'content': { 'required': False },
            'origin': { 'required': False }
        }





class OrderPlannerUpdateSerializer(OrderSerializer):
    payment_date = serializers.DateField(write_only=True)
    
    class Meta:
        fields = ('payment_date',)

    def update(self, instance, validated_data):
        #set payment date
        payment_date = validated_data.pop('payment_date')
        return instance.save(status=2)





class OrderManagementUpdateSerializer(OrderSerializer):
    agreement = serializers.BooleanField(write_only=True)
    
    class Meta:
        fields = ('agreement',)

    def update(self, instance, validated_data):
        agreement = validated_data.pop('agreement')
        new_status = 2 if agreement else 5
        return instance.save(status=new_status)





class OrderExecutorUpdateSerializer(OrderSerializer):
    deadline = serializers.DateField(required=False)

    class Meta:
        fields = ('status', 'stage', 'priority', 'origin', 'deadline',)

    def validate(self, data):
        instance = self.instance
        #check the status
        if 'status' in data:
            if instance.status == Status.NEW and data['status'] != Status.PROCESSING:
                raise serializers.ValidationError({
                    'status': 'Wrong value. You must pass 2 for this status'
                })
            elif instance.status == Status.PROCESSING and data['status'] not in [Status.PAYMENT_AWAIT, Status.APPROVAL_AWAIT, Status.FINISHED]:
                raise serializers.ValidationError({
                    'status': 'Wrong value. You must pass 3, 4 or 6 for this status'
                })
        #check the stage
        if 'stage' in data:
            if not data['deadline']:
                raise serializers.ValidationError({
                    'stage': 'If you want to change stage, you must pass a deadline parameter for new stage'
                })
            if instance.stage + 1 != data['stage']:
                raise serializers.ValidationError({
                    'stage': f'Wrong value. You must pass value {instance.stage + 1} for this stage'
                })
        return data
        
    def update(self, instance, validated_data):
        if 'status' in validated_data and validated_data['status'] == Status.PROCESSING:
            #set stage on 'In planning'
            validated_data['stage'] = Stage.PLAN
        return instance.save(**validated_data)