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


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Model for Role
    """
    list_display = ("id", "role")
    search_fields = ("role", )


admin.site.unregister(Group)
