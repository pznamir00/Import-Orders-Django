from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('role',)


class UserDetailSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    class Meta:
        model = User
        fields = ('email', 'username', 'profile',)