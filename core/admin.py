from django.contrib import admin

# Register your models here.
from core.models import EventStatus, EventType, Promotion, Event


@admin.register(EventStatus)
class EventStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "type")
    search_fields = ("type", )


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "type")
    search_fields = ("type", )


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ("id", "discount_percentage", "channel")
    search_fields = ("discount_percentage", "channel")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "type", "date", "time", "location", "subscription_fee", "no_of_tickets", "status")
    search_fields = ("name", "type", "status")


