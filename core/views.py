import json
from datetime import date

from django.db import transaction
from django.db.models import ExpressionWrapper, IntegerField
from django.db.models import F
from rest_framework import mixins, generics
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from core.models import Event, Subscription, EventStatus
from core.serializers import EventSerializer, SubscriptionSerializer, ListUpdateEventSerializer
# Create your views here.
from eon_backend import settings
from utils.common import api_success_response, api_error_response


class EventViewSet(ModelViewSet):
    authentication_classes = (JWTAuthentication,)
    queryset = Event.objects.all().select_related('type').annotate(event_type=F('type__type'))
    serializer_class = ListUpdateEventSerializer

    def list(self, request, *args, **kwargs):
        location = request.GET.get("location", None)
        event_type = request.GET.get("event_type", None)
        start_date = request.GET.get("start_date", None)
        end_date = request.GET.get("end_date", None)
        today = date.today()
        status = EventStatus.objects.get(type__iexact="Cancelled")
        self.queryset.filter(date__lt=str(today)).update(status=status.id)
        self.queryset = self.queryset.filter(date__gte=str(today))
        if location:
            self.queryset = self.queryset.filter(location__iexact=location, status__type='ACTIVE')
        if event_type:
            self.queryset = self.queryset.filter(type=event_type, status__type='ACTIVE')
        if start_date and end_date:
            self.queryset = self.queryset.filter(date__range=[start_date, end_date], status__type='ACTIVE')
        if len(self.queryset) > 1:
            self.queryset = self.queryset.annotate(diff=ExpressionWrapper(
                         F('sold_tickets')*100000/F('no_of_tickets'), output_field=IntegerField()))
            self.queryset = self.queryset.order_by('-diff')
        return super(EventViewSet, self).list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        self.serializer_class = EventSerializer
        return super(EventViewSet, self).create(request, *args, **kwargs)


class SubscriptionViewSet(mixins.CreateModelMixin, generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    @transaction.atomic()
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
        user_id = data.get('user_id', None)
        # getting user_id from token

        data = dict(user=user_id, event=event_id, no_of_tickets=no_of_tickets, payment_id=payment_id)
        try:
            event = Event.objects.get(id=event_id)
        except:
            return api_error_response(message="Invalid event_id", status=400)

        if event.no_of_tickets-event.sold_tickets >= no_of_tickets:
            event.sold_tickets += no_of_tickets
            event.save()

            serializer = SubscriptionSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return api_success_response(message="Subscribed Successfully", status=201)
        else:
            return api_error_response(message="Number of tickets are invalid", status=400)
