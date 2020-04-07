
import json

from django.db.models import F
from rest_framework import mixins, generics
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from core.models import Event, Subscription, EventType
from core.serializers import EventSerializer, SubscriptionSerializer, ListUpdateEventSerializer, EventTypeSerializer

from utils.common import api_success_response, api_error_response
from utils.helper import send_email_sms_and_notification


from core.models import UserProfile
from core.serializers import UserProfileSerializer

# Create your views here.


class UserViewSet(ModelViewSet):
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
        data = json.loads(request.body)
        event_id = data.get('event_id', None)
        no_of_tickets = data.get('no_of_tickets', None)
        payment_id = data.get('payment_id', None)
        user_id = data.get('user_id', None)
        # getting user_id from token

        data = dict(user=user_id, event=event_id, no_of_tickets=no_of_tickets, payment_id=payment_id)
        try:
            event = Event.objects.get(id=event_id)
        except:
            return api_error_response(message="Invalid event_id", status=400)

        if event.no_of_tickets - event.sold_tickets >= no_of_tickets:
            event.sold_tickets += no_of_tickets
            event.save()

            serializer = SubscriptionSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return api_success_response(message="Subscribed Successfully", status=201)
        else:
            return api_error_response(message="Number of tickets are invalid", status=400)


class EventTypeView(APIView):

    def get(self, request):
        event_type = EventType.objects.all()
        serializer = EventTypeSerializer(event_type, many=True)
        return api_success_response(data=serializer.data)


class SubscriberReminder(mixins.ListModelMixin, generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    queryset = Subscription.objects.all()

    def get(self, request):
        event_id = request.GET.get("event_id", None)
        if event_id:
            event_name = Event.objects.values_list("name", flat=True).get(id=event_id)
            if event_name:
                self.queryset = self.queryset.filter(event=event_id)
                response = self.queryset.select_related('user').annotate(email=F('user__email')).values("email")
                email_ids = [_["email"] for _ in response]
                send_email_sms_and_notification(event_name="event_reminder",
                                                email_ids=email_ids,
                                                message=f"A Gentle reminder for the {event_name}")
                return api_success_response(message="Reminder sent successfully to all the subscribers.")

        return self.update(request)

