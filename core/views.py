from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from core.models import Event
from core.serializers import EventSerializer
from datetime import timedelta, datetime, date
import calendar
# Create your views here.


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
        if location:
            self.queryset = self.queryset.filter(location__iexact=location, status__type='ACTIVE')
        if event_type:
            self.queryset = self.queryset.filter(type=event_type, status__type='ACTIVE')
        if start_date and end_date:
            self.queryset = self.queryset.filter(date__range=[start_date, end_date], status__type='ACTIVE')
        return super(EventViewSet, self).list(request, *args, **kwargs)
