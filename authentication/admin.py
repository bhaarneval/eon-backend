from django.contrib import admin
from django.contrib.auth.models import Group

from .models import User, Role


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email")
    search_fields = ("email", )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "role")
    search_fields = ("role", )


admin.site.unregister(Group)


