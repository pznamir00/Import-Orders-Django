from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('role',)


class UserDetailSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'is_superuser', 'profile', 'password',)

    def create(self, validated_data):
        """
        Only admin can add new user in this point
        with all necessery data like password or role.
        """
        profile = validated_data.pop('profile')
        validated_data['password'] = make_password(validated_data.get('password'))
        user = User.objects.create_user(**validated_data)
        profile = UserProfile.objects.create(
            user=user,
            role=profile['role']
        )
        return user
