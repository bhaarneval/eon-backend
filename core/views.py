import json

from django.db.models import F
from rest_framework import mixins, generics
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Event, Subscription, EventType, UserProfile
from core.serializers import SubscriptionSerializer, EventTypeSerializer, UserProfileSerializer
from rest_framework.decorators import authentication_classes, permission_classes, api_view


from utils.common import api_success_response, api_error_response
from utils.helper import send_email_sms_and_notification

# TODO: If this piece of code is used anywhere then remove this and unused import also.
# class UserViewSet(ModelViewSet):
#     authentication_classes = (JWTAuthentication,)
#     queryset = UserProfile.objects.all()
#     serializer_class = UserProfileSerializer
#
#     def put(self, request):
#         """
#         Function to update the user_details
#         :param request: will contain user_id and details that need to be updated as
#         {
#             'user': <int:id>
#             fields to be updated in same json format
#         }
#         :return: Updated UserProfile object as response or error_message if failed
#         """
#         data = json.loads(request.body)
#         event_id = data.get('event_id', None)
#         no_of_tickets = data.get('no_of_tickets', None)
#         payment_id = data.get('payment_id', None)
#         user_id = data.get('user_id', None)
#         # getting user_id from token
#
#         data = dict(user=user_id, event=event_id, no_of_tickets=no_of_tickets, payment_id=payment_id)
#         try:
#             event = Event.objects.get(id=event_id)
#         except:
#             return api_error_response(message="Invalid event_id", status=400)
#
#         if event.no_of_tickets - event.sold_tickets >= no_of_tickets:
#             event.sold_tickets += no_of_tickets
#             event.save()
#
#             serializer = SubscriptionSerializer(data=data)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#
#             return api_success_response(message="Subscribed Successfully", status=201)
#         else:
#             return api_error_response(message="Number of tickets are invalid", status=400)
#


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
