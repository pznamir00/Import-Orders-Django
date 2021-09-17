from django.db import models

class UserRole(models.TextChoices):
    CLIENT = '1', 'Client'
    EXECUTOR = '2', 'Executor'
    PLANNER = '3', 'Planner'
    MANAGEMENT = '4', 'Management'