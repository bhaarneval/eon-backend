from django.contrib import admin

# Register your models here.
from payment.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "type",'amount', 'discount_amount', 'total_amount', 'status', 'ref_number', 'invoice')
    search_fields = ("type", 'status')

