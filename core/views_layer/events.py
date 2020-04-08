from datetime import date

from django.db.models import ExpressionWrapper, F, IntegerField
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Event
from core.serializers import ListUpdateEventSerializer, EventSerializer


class EventViewSet(ModelViewSet):
    authentication_classes = (JWTAuthentication,)
    queryset = Event.objects.all().select_related('type').annotate(event_type=F('type__type'))
    serializer_class = ListUpdateEventSerializer

    def list(self, request, *args, **kwargs):
        location = request.GET.get("location", None)
        event_type = request.GET.get("event_type", None)
        start_date = request.GET.get("start_date", None)
        end_date = request.GET.get("end_date", None)
        user_id = request.GET.get('event_created_by', None)
        today = date.today()
        self.queryset.filter(date__lt=str(today)).update(is_cancelled=True)
        self.queryset = self.queryset.filter(date__gte=str(today))
        if location:
            self.queryset = self.queryset.filter(location__iexact=location)
        if user_id:
            self.queryset = self.queryset.filter(event_created_by=user_id)
        if event_type:
            self.queryset = self.queryset.filter(type=event_type)
        if start_date and end_date:
            self.queryset = self.queryset.filter(date__range=[start_date, end_date])
        if len(self.queryset) > 1:
            self.queryset = self.queryset.annotate(diff=ExpressionWrapper(
                F('sold_tickets')*100000/F('no_of_tickets'), output_field=IntegerField()))
            self.queryset = self.queryset.order_by('-diff')
        return super(EventViewSet, self).list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        self.serializer_class = EventSerializer
        return super(EventViewSet, self).create(request, *args, **kwargs)
