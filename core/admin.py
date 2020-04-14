from daterangefilter.filters import PastDateRangeFilter
from django.contrib import admin

# Register your models here.

from core.models import EventType, Event, Invitation, EventPreference, Subscription, UserProfile, WishList, Notification


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "type")
    search_fields = ("type",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name", "type", "date", "time", "location", "subscription_fee", "no_of_tickets", "sold_tickets",
        "is_cancelled", "event_created_by")
    search_fields = ("name", "type__type", "event_created_by__email", "event_created_by__userprofile__name")
    list_filter = ("type", "event_created_by", ("date", PastDateRangeFilter))
    fieldsets = (
        (
            "", {
                'fields': (
                    "name", "type", "description", "date", "time", "location", "images", "subscription_fee",
                    "no_of_tickets", "external_links", "event_created_by", "sold_tickets", "is_active", "is_cancelled")
            }
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["images", "sold_tickets", "event_created_by"]
        else:
            return ["sold_tickets", "images", "is_active", "is_cancelled"]


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "user", "discount_percentage", "email")
    search_fields = ("event__name", "user__email", "user__userprofile__name",)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(EventPreference)
class EventPreferenceAdmin(admin.ModelAdmin):
    list_display = ("id", "event_type", "user")
    search_fields = ("event_type__type", "user__email", "user__userprofile__name",)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "user", "no_of_tickets", "payment", 'is_active')
    search_fields = ("event__name", "user__email")
    readonly_fields = ("event", "user", "no_of_tickets", "payment")

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(WishList)
class WishListAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "user", "is_active")
    search_fields = ("event__name", "user__email", "user__userprofile__name",)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "contact_number", "organization", "role")
    search_fields = ("user__email", "user__userprofile__name", "contact_number", "organization", "role")
    readonly_fields = ('user',)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "event", "message", "has_read")
    search_fields = ("user__email", "user__userprofile__name", "event__name", "message", "has_read")

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
