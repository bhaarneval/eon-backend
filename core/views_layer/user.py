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

    def put(self, request):
        """
        Function to update the user_details
        :param request: will contain user_id and details that need to be updated as
        {
            'user': <int:id>
            fields to be updated in same json format
        }
        :return: Updated UserProfile object as response or error_message if failed
        """
        return self.update(request)
