from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register('orders', views.OrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router.urls))
]