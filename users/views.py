from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import UserDetailSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import CreateOnlyForAdmin



class UserDetailView(generics.RetrieveAPIView, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = (IsAuthenticated, CreateOnlyForAdmin,)

    def get_object(self):
        return self.request.user