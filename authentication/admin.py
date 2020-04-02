from django.contrib import admin
from .models import User, UserDetails, Status, Role


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email")
    search_fields = ("email", )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "role")
    search_fields = ("role", )


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("id", "status")
    search_fields = ("status", )


@admin.register(UserDetails)
class UserDetailsAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "contact_number", "organization", "status", "role")
    search_fields = ("user", "contact_number", "organization", "status", "role")

