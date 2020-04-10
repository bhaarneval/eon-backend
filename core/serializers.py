from rest_framework import serializers
from core.models import Event, Subscription, UserProfile, Invitation, EventType, WishList


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
                  'external_links',
                  'event_created_by')


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        exclude = ('created_on', 'updated_on')


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
    paid_amount = serializers.IntegerField()

    class Meta:
        model = Subscription
        fields = ('name',
                  'email',
                  'no_of_tickets',
                  'paid_amount')


class InvitationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Invitation
        fields = "__all__"


class EventTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventType
        exclude = ('created_on', 'updated_on')


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = "__all__"


class WishListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishList
        exclude = ('created_on', 'updated_on', 'is_active')
