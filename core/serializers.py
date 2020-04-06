from rest_framework import serializers
from core.models import Event, Subscription, Invitation


class ListUpdateEventSerializer(serializers.ModelSerializer):
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
        fields = ('user',
                  'event',
                  'no_of_tickets',
                  'payment')


class SubscriptionListSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    discount = serializers.IntegerField()

    class Meta:
        model = Subscription
        fields = ('name',
                  'email',
                  'no_of_tickets',
                  'discount')


class InvitationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Invitation
        fields = "__all__"

