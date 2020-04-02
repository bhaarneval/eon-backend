from django.contrib import admin
from .models import User, UserDetails, Status, Role


class UserAdmin(admin.ModelAdmin):
    class Meta:
        model = User


admin.site.register(User, UserAdmin)


class RoleAdmin(admin.ModelAdmin):
    class Meta:
        model = Role


admin.site.register(Role, RoleAdmin)


class StatusAdmin(admin.ModelAdmin):
    class Meta:
        model = Status


admin.site.register(Status, StatusAdmin)


class UserDetailsAdmin(admin.ModelAdmin):
    class Meta:
        model = UserDetails


admin.site.register(UserDetails, UserDetailsAdmin)
