from rest_framework.permissions import BasePermission, SAFE_METHODS
from core.models import UserProfile


class IsOrganiserOrReadOnlySubscriber(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return UserProfile.objects.get(user=request.user).role.role in ['organiser', 'admin']

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user


class IsOrganiser(BasePermission):

    def has_permission(self, request, view):
        return UserProfile.objects.get(user=request.user).role.role in ["organiser", "admin"]


class IsSubscriberOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return UserProfile.objects.get(user=request.user).role.role == "subscriber"


class IsOwnerOrNotSubscriber(BasePermission):

    def has_permission(self, request, view):
        if UserProfile.objects.get(user=request.user).role.role == "subscriber":
            if view.action == "list":
                return False
        return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user
