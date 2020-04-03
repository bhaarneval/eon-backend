from django.contrib import admin

# Register your models here.
from payment.models import Payment, PaymentType


@admin.register(Payment)
class EventStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "type", 'discount', 'status')
    search_fields = ("type", 'status')


@admin.register(PaymentType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "type")
    search_fields = ("type", )
