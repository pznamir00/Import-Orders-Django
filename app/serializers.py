from rest_framework import serializers
from .models import Order, OrderLog, OrderComment



class OrderLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLog
        fields = '__all__'



class OrderCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderComment
        fields = '__all__'



class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('title', 'status', 'stage', 'executor',)



class OrderDetailSerializer(serializers.ModelSerializer):
    logs = OrderLogSerializer(many=True, read_only=True)
    comments = OrderCommentSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = '__all__'