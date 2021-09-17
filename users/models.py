from django.db import models
from django.contrib.auth.models import User
from .choices import UserRole


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=1, choices=UserRole.choices)

    def __str__(self):
        return self.user.username + ' user profile'