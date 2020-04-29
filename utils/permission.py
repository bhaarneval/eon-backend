"""
Custom based permissions for each function
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS
from core.models import UserProfile


class IsOrganizerOrReadOnlySubscriber(BasePermission):
    """
    Permission class to check whether that person is organizer,
    or allowing SAFE_METHODS for subscriber
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return UserProfile.objects.get(user=request.user).role.role in ['organizer', 'admin']

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user


class IsOrganizer(BasePermission):
    """
        Permission class to check whether the person is organizer or admin
    """

    def has_permission(self, request, view):
        return UserProfile.objects.get(user=request.user).role.role in ["organizer", "admin"]


class IsSubscriberOrReadOnly(BasePermission):
    """
        Permission class to check whether the person is subscriber,
        or allowing SAFE_METHODS for others
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return UserProfile.objects.get(user=request.user).role.role == "subscriber"


class IsOwnerOrNotSubscriber(BasePermission):
    """
        Permission class to check whether the person is owner,
        or allowing retrieve for subscriber
    """

    def has_permission(self, request, view):
        if UserProfile.objects.get(user=request.user).role.role == "subscriber":
            if view.action == "list":
                return False
        return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user
