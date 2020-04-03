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
        events = request.GET.get("events", None)
        if location:
            self.queryset = self.queryset.filter(location__iexact=location)
        if event_type:
            self.queryset = self.queryset.filter(type=event_type)
        if events:
            dt = datetime.strptime(str(date.today()), '%Y-%m-%d')
            if events == "daily":
                self.queryset = self.queryset.filter(date=events)
            elif events == 'weekly':
                start = dt - timedelta(days=dt.weekday())
                end = start + timedelta(days=6)
                self.queryset = self.queryset.filter(date__range=[str(start.date()), str(end.date())])
            elif events == 'monthly':
                year = dt.year
                month = dt.month
                month_start_end_date = calendar.monthrange(year, month)
                month_start_date = "{}-{}-{}".format(year, month_start_end_date[0], month)
                month_end_date = "{}-{}-{}".format(year, month_start_end_date[1], month)
                self.queryset = self.queryset.filter(date__range=[month_start_date, month_end_date])

        return super(EventViewSet, self).list(request, *args, **kwargs)
