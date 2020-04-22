"""
Added model for admin view so admin user can see the model and can update also
"""
from django.contrib import admin
from django.contrib.auth.models import Group
from django.db.models.signals import post_save, post_init

from utils.helper import send_email_sms_and_notification
from .models import User
from .signals import post_save_method, remember_state_method


def block_user(modelAdmin, request, queryset):
    queryset.update(is_active=False)
    email_ids = queryset.values_list('email', flat=True)
    send_email_sms_and_notification(action_name="user_blocked",
                                    email_ids=email_ids)


block_user.short_description = "Block selected Users"


def unblock_user(modelAdmin, request, queryset):
    queryset.update(is_active=True)
    email_ids = queryset.values_list('email', flat=True)
    send_email_sms_and_notification(action_name="user_unblocked",
                                    email_ids=email_ids)


unblock_user.short_description = "Activate selected Users"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Model for user Admin
    """
    actions = (block_user, unblock_user)
    list_display = ("id", "email")
    search_fields = ("email",)
    list_filter = ("is_active",)
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


post_save.connect(post_save_method, sender=User)
post_init.connect(remember_state_method, sender=User)

admin.site.unregister(Group)
