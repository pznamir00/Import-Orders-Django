from django.db import models
from django.contrib.auth.models import User
from .choices import Status, Priority, Stage, Origin, Event



class Order(models.Model):
    title = models.CharField(max_length=64)
    content = models.TextField()
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.NEW)
    priority = models.CharField(max_length=2, choices=Priority.choices, default=Priority.LOW)
    stage = models.CharField(max_length=2, choices=Stage.choices, blank=True, null=True)
    origin = models.CharField(max_length=2, choices=Origin.choices)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    executor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='executing_orders')

    def __str__(self):
        return self.title



class Log(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='logs')
    event = models.CharField(max_length=2, choices=Event.choices)
    recorded_time = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(blank=True, null=True)

    def __str__(self):
        return 'Order #' + str(self.order.pk) + f' Log ({self.event})'



class Comment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)