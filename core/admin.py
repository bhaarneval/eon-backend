from django.contrib import admin

# Register your models here.
from core.models import EventStatus, EventType, Event, Invitation, EventPreference, Subscription, UserProfile


@admin.register(EventStatus)
class EventStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "type")
    search_fields = ("type", )


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "type")
    search_fields = ("type", )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "type", "date", "time", "location", "subscription_fee", "no_of_tickets", "status")
    search_fields = ("name", "type", "status")


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "user", "discount_percentage")
    search_fields = ("event", "user")


@admin.register(EventPreference)
class EventPreferenceAdmin(admin.ModelAdmin):
    list_display = ("id", "event_type", "user")
    search_fields = ("event_type", "user")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "user", "no_of_tickets", "payment")
    search_fields = ("event", "user")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "contact_number", "organization", "role")
    search_fields = ("user", "contact_number", "organization", "role")
