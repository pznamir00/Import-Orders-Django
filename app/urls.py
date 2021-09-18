from django.urls import include, path
from rest_framework_extensions.routers import ExtendedSimpleRouter
from . import views

router = ExtendedSimpleRouter()
(
    router.register(
        r'orders', 
        views.OrderViewSet, 
        basename='orders'
    ).register(
        r'comments', 
        views.OrderCommentViewSet, 
        basename='comments', 
        parents_query_lookups=['order']
    )
)

urlpatterns = router.urls