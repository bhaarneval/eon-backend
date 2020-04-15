"""
Added core related api view here
"""
import json

from django.db.models import F
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Event, Subscription, EventType
from core.serializers import EventTypeSerializer
from eon_backend.settings import EVENT_URL

from utils.common import api_success_response, api_error_response
from utils.helper import send_email_sms_and_notification


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_event_types(request):
    """
    Get api method for event type
    """
    event_type = EventType.objects.filter(is_active=True)
    serializer = EventTypeSerializer(event_type, many=True)
    return api_success_response(data=serializer.data)


class SubscriberNotify(APIView):
    """
        Created api method related to subscriber
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Subscription.objects.filter(is_active=True)

    def post(self, request):
        """
        Post api method for subscriber notify
        """
        data = request.data
        event_id = data.get("event_id", None)
        message = data.get("message", "")
        _type = data.get("type", "reminder").lower()
        if event_id:
            event_name = Event.objects.values_list("name", flat=True).get(id=event_id)
            if event_name:
                self.queryset = self.queryset.filter(event=event_id)
                response = self.queryset.select_related('user'). \
                    annotate(email=F('user__email'),
                             users_id=F('user__id')).values("email",
                                                            "users_id")
                email_ids = [_["email"] for _ in response]
                user_ids = [_["users_id"] for _ in response]
                if _type == "reminder":
                    action_name = "event_reminder"
                else:
                    action_name = "send_updates"
                send_email_sms_and_notification(action_name=action_name,
                                                email_ids=email_ids,
                                                message=message,
                                                event_name=event_name,
                                                user_ids=user_ids,
                                                event_id=event_id)
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
    event_id = data.get("event_id")
    if not (event_id and email):
        return api_error_response(message="Please provide necessary details", status=400)
    if isinstance(email, str):
        email = [email]
    message = data.get("message")
    try:
        event_name = Event.objects.get(id=event_id).name
    except Event.DoesNotExist:
        return api_error_response(message="Invalid email id", status=400)
    send_email_sms_and_notification(action_name="user_share",
                                    message=message,
                                    url=EVENT_URL+str(event_id),
                                    event_name=event_name,
                                    email_ids=email)
    return api_success_response(message="Mail send successfully", status=200)
