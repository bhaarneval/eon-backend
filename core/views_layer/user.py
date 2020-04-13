"""
User related functions are here
"""
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import UserProfile
from core.serializers import UserProfileSerializer


class UserViewSet(ModelViewSet):
    """
    user update function in this class
    """
    authentication_classes = (JWTAuthentication,)
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = "user_id"
