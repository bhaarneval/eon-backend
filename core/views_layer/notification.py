import jwt

from rest_framework.views import APIView
from rest_framework.authentication import get_authorization_header
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Notification
from core.serializers import NotificationSerializer
from eon_backend.settings import SECRET_KEY

from utils.common import api_success_response, api_error_response


class NotificationView(APIView):
    """API for Notification"""

    serializer_class = NotificationSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )
    queryset = Notification.objects.all()

    def patch(self, request):

        list_of_ids = request.data.get('notification_ids')

        try:
            self.queryset.filter(id__in=list_of_ids).update(has_read=True)
        except:
            api_error_response(message="Something went wrong", status=500)

        return api_success_response(message="Notification updated successfully", status=200)

    def get(self, request):

        token = get_authorization_header(request).split()[1]
        payload = jwt.decode(token, SECRET_KEY)
        user_id = payload['user_id']

        try:
            notifications = self.queryset.filter(user=user_id, has_read=False)

        except Notification.DoesNotExist:
            notifications = []

        serializer = self.serializer_class(notifications, many=True)
        return api_success_response(data=serializer.data)
