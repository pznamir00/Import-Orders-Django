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

urlpatterns = [
    path('statuses/', views.StatusView.as_view()),
    path('stages/', views.StageView.as_view()),
    path('priorities/', views.PriorityView.as_view()),
    path('origins/', views.OriginView.as_view()),
    path('', include(router.urls))
]