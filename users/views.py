from rest_framework import generics
from .models import UserProfile
from django.contrib.auth.models import User
from .serializers import UserDetailSerializer
from rest_framework.permissions import IsAuthenticated



class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user