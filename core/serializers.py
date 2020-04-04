from rest_framework import serializers
from core.models import Event, Subscription


class ListEventSerializer(serializers.ModelSerializer):
    event_type = serializers.CharField()

    class Meta:
        model = Event
        fields = ('id',
                  'name',
                  'date',
                  'time',
                  'location',
                  'event_type',
                  'description',
                  'no_of_tickets',
                  'subscription_fee',
                  'images',
                  'external_links')


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = "__all__"

