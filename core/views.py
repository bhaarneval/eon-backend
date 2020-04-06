import json

import jwt
from rest_framework import mixins, generics
from rest_framework.authentication import get_authorization_header
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from core.models import Event, EventStatus, Subscription, UserProfile
from core.serializers import EventSerializer, SubscriptionSerializer, UserProfileSerializer
from datetime import date

from eon_backend import settings
from utils.common import api_success_response, api_error_response


class EventViewSet(ModelViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def list(self, request, *args, **kwargs):
        location = request.GET.get("location", None)
        event_type = request.GET.get("event_type", None)
        start_date = request.GET.get("start_date", None)
        end_date = request.GET.get("end_date", None)
        today = date.today()
        status = EventStatus.objects.get(type__iexact="Cancelled")
        self.queryset = self.queryset.filter(date__lt=str(today))
        self.queryset.update(status=status.id)
        if location:
            self.queryset = self.queryset.filter(location__iexact=location, status__type='ACTIVE', date__gt=str(today))
        if event_type:
            self.queryset = self.queryset.filter(type=event_type, status__type='ACTIVE', date__gt=str(today))
        if start_date and end_date:
            self.queryset = self.queryset.filter(date__range=[start_date, end_date], status__type='ACTIVE')
        # self.queryset = self.
        return super(EventViewSet, self).list(request, *args, **kwargs)


class SubscriptionViewSet(mixins.CreateModelMixin, generics.GenericAPIView):

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def post(self, request):
        """
            Function to set subscription of a user to a particular event
            :param request: token, event_id, no_of_tickets, payment
            :return: json response subscribed successful or error message
        """
        data = json.loads(request.body)
        event_id = data.get('event_id', None)
        no_of_tickets = data.get('no_of_tickets', None)
        payment_id = data.get('payment_id', None)

        # getting user_id from token

        token = get_authorization_header(request).decode('utf-8').split(" ")[1]
        decode = jwt.decode(token, settings.SECRET_KEY)
        user_id = decode.get('user_id', None)

        data = dict(user=user_id, event=event_id, no_of_tickets=no_of_tickets, payment_id=payment_id)

        serializer = SubscriptionSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return api_success_response(message="Subscribed Successfully", status=201)


class UserViewSet(ModelViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
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

