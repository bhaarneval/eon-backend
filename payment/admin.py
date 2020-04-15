"""
 Register your models here.
"""
from django.contrib import admin

# Register your models here.
from payment.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Method to show filds for admin
    """
    list_display = ("id", 'amount', 'discount_amount', 'total_amount', 'status', 'ref_number')
    list_filter = ("status",)
    search_fields = ('id', 'status', 'ref_number')
    readonly_fields = ('amount', 'discount_amount', 'total_amount', 'status', 'ref_number')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
