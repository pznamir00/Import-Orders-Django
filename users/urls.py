from django.urls import include, path
from . import views


urlpatterns = [
    path('user/', views.UserDetailView.as_view()),
    path('', include('rest_auth.urls'))
]