"""
all core module serializer classes are here
"""
from rest_framework import serializers
from core.models import Event, Subscription, UserProfile,\
    Invitation, EventType, WishList, Notification


class ListUpdateEventSerializer(serializers.ModelSerializer):
    """
    serializer class for  event list
    """
    event_type = serializers.CharField()

    class Meta:
        """
        To override the database table name, use the db_table parameter in class Meta.
        """
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
    """
    serializer class for model Event
    """

    class Meta:
        """
        To override the database table name, use the db_table parameter in class Meta.
        """
        model = Event
        exclude = ('created_on', 'updated_on')


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    serializer class for model subscription
    """

    class Meta:
        """
        To override the database table name, use the db_table parameter in class Meta.
        """
        model = Subscription
        fields = ('user',
                  'event',
                  'no_of_tickets',
                  'payment')


class SubscriptionListSerializer(serializers.ModelSerializer):
    """
    serializer class for  subscription list
    """
    name = serializers.CharField()
    email = serializers.EmailField()
    paid_amount = serializers.IntegerField()

    class Meta:
        """
        To override the database table name, use the db_table parameter in class Meta.
        """
        model = Subscription
        fields = ('name',
                  'email',
                  'no_of_tickets',
                  'paid_amount')


class InvitationSerializer(serializers.ModelSerializer):
    """
    invitation serializer class
    """

    class Meta:
        """
        To override the database table name, use the db_table parameter in class Meta.
        """
        model = Invitation
        fields = "__all__"


class EventTypeSerializer(serializers.ModelSerializer):
    """
    serializer class for model event type
    """

    class Meta:
        """
        class Meta:To override the database table name,
         use the db_table parameter in class Meta.
        """
        model = EventType
        exclude = ('created_on', 'updated_on', 'is_active')


class UserProfileSerializer(serializers.ModelSerializer):
    """
    serializer class for model user profile
    """

    class Meta:
        """
        class Meta:To override the database table name,
        use the db_table parameter in class Meta.

        """
        model = UserProfile
        fields = "__all__"


class WishListSerializer(serializers.ModelSerializer):
    """
    Serializer class for model wish list
    """
    class Meta:
        """
            class Meta:To override the database table name,
            use the db_table parameter in class Meta.
        """
        model = WishList
        exclude = ('created_on', 'updated_on', 'is_active')


class NotificationSerializer(serializers.ModelSerializer):
    """
    serializer class for notification model
    """
    class Meta:
        """
        class Meta:To override the database table name,
        use the db_table parameter in class Meta.
        """
        model = Notification
        fields = "__all__"
