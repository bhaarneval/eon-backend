import json

from django.db.models import F
from rest_framework import mixins, generics
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from core.models import Event, Subscription, EventType, Notification
from core.serializers import EventTypeSerializer, NotificationSerializer


from utils.common import api_success_response, api_error_response
from utils.helper import send_email_sms_and_notification


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_event_types(request):
    event_type = EventType.objects.all()
    serializer = EventTypeSerializer(event_type, many=True)
    return api_success_response(data=serializer.data)


class SubscriberNotify(mixins.ListModelMixin, generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Subscription.objects.all()

    def post(self, request):
        data = json.loads(request.data)
        event_id = data.get("event_id", None)
        message = data.get("message", "")
        _type = data.get("type", "reminder").lower()
        if event_id:
            event_name = Event.objects.values_list("name", flat=True).get(id=event_id)
            if event_name:
                self.queryset = self.queryset.filter(event=event_id)
                response = self.queryset.select_related('user').annotate(email=F('user__email')).values("email", "id")
                email_ids = [_["email"] for _ in response]
                user_ids = [_["id"] for _ in response]
                if _type == "reminder":
                    action_name = "event_reminder"
                else:
                    action_name = "send_updates"
                send_email_sms_and_notification(action_name=action_name,
                                                email_ids=email_ids,
                                                message=message,
                                                user_ids=user_ids)
                return api_success_response(message="Subscribers notified successfully.")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def send_mail_to_a_friend(request):
    """
        Function to send mail to an email_id.
        :param request: email_id: email_id of a friend list_object or string
        :return:
    """

    data = json.loads(request.body)
    email = data.get("email_id")
    if isinstance(email, str):
        email = [email]
    message = data.get("message")
    send_email_sms_and_notification(action_name="user_share",
                                    message=message,
                                    email_ids=email)
    return api_success_response(message="Mail send successfully", status=200)


class NotificationView(APIView):
    """API for Notification"""

    serializer_class = NotificationSerializer

    def patch(self, request):

        list_of_ids = request.data.get('notification_id')

        for notification_id in list_of_ids:
            try:
                notification = Notification.objects.get(id=notification_id)
                notification.has_read = True
                notification.save()
            except:
                api_error_response("Notification Id ={id} does not exist".format(id=notification_id), 400)

        return api_success_response(message="Unread notification updated successfully", status=200)

    def get(self, request):

        user_id = request.GET.get('user_id', None)

        if user_id is not None:
            try:
                notifications = Notification.objects.filter(user=user_id, has_read=False)

            except:
                return api_error_response(message="Notification for this user is not exist", status=400)
        else:
            return api_error_response(message="user ID can not be null", status=400)
        json_list = []
        for notification in notifications:
            notification_obj = {
                "message": notification.message,
                "notification_id": notification.id
            }
            json_list.append(notification_obj)

        return api_success_response(data=json_list)
