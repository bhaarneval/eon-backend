from django.contrib import admin
from django.db.models import Q

from core.models import Event


class PaidFreeEventFilter(admin.SimpleListFilter):
    """
    Filter for the free or paid event
    """
    title = "Paid Free filter"
    parameter_name = "subscription_fee"

    def lookups(self, request, model_admin):
        return [('free', 'Free'), ('paid', 'Paid')]

    def queryset(self, request, queryset):
        if self.value() == 'free':
            return queryset.filter(subscription_fee=0)
        elif self.value() == 'paid':
            return queryset.filter(~Q(subscription_fee=0))

