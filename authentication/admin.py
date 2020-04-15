"""
Added model for admin view so admin user can see the model and can update also
"""
from django.contrib import admin
from django.contrib.auth.models import Group

from .models import User, Role


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Model for user Admin
    """
    list_display = ("id", "email")
    search_fields = ("email",)
    readonly_fields = ('email',)
    fieldsets = (
        (
            "", {
                "fields": ('email', 'is_active')
            }
        ),
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


admin.site.unregister(Group)
