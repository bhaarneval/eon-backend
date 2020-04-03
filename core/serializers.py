from rest_framework import serializers
from core.models import Event, Subscription


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = "__all__"

