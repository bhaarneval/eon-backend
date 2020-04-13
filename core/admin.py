"""
register all the core related model here
"""
from django.contrib import admin

# Register your models here.
from core.models import EventType, Event, Invitation, EventPreference, Subscription, UserProfile


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    """
    added event type model in admin
    """
    list_display = ("id", "type")
    search_fields = ("type",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    added event model in admin
    """
    list_display = (
        "id", "name", "type", "date", "time", "location", "subscription_fee",
        "no_of_tickets", "sold_tickets", "is_cancelled")
    search_fields = ("name", "type", "event_created_by")


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    """
    added invitation in admin
    """
    list_display = ("id", "event", "user", "discount_percentage", "email")
    search_fields = ("event", "user")


@admin.register(EventPreference)
class EventPreferenceAdmin(admin.ModelAdmin):
    """
    added event preference in admin
    """
    list_display = ("id", "event_type", "user")
    search_fields = ("event_type", "user")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    added subscription model in admin
    """
    list_display = ("id", "event", "user", "no_of_tickets", "payment", 'is_active')
    search_fields = ("event", "user")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    added user profile model in admin
    """
    list_display = ("id", "user", "contact_number", "organization", "role")
    search_fields = ("user", "contact_number", "organization", "role")
