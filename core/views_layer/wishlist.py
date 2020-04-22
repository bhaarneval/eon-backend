"""
All wish list related methods are here
"""
import json

import jwt
from django.db import transaction
from rest_framework import viewsets
from rest_framework.authentication import get_authorization_header
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import WishList, Event
from core.serializers import WishListSerializer
from eon_backend.settings import SECRET_KEY
from utils.common import api_error_response, api_success_response
from utils.permission import IsSubscriberOrReadOnly


class WishListViewSet(viewsets.ViewSet):
    """
    Wish list api created in this class
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, IsSubscriberOrReadOnly)
    queryset = WishList.objects.filter(is_active=True)

    @transaction.atomic()
    def create(self, request):
        """
        Create api for wish list
        """
        data = json.loads(request.body)
        event_id = data.get('event_id', None)
        token = get_authorization_header(request).split()[1]
        payload = jwt.decode(token, SECRET_KEY)
        user_id = payload['user_id']

        if user_id and event_id:
            data = dict(user=user_id, event=event_id)
            wishlist = None
            try:
                event = Event.objects.get(id=event_id, is_active=True)
            except:
                return api_error_response(message="Invalid Event", status=400)

            if event and event.event_created_by == user_id:
                return api_error_response(message="You are the Organizer of the event", status=400)

            try:
                wishlist = WishList.objects.get(user=user_id, event=event_id)
            except:
                pass
            if wishlist:
                if not wishlist.is_active:
                    wishlist.is_active = True
                    wishlist.save()
                    message = "WishListed Successfully"
                else:
                    message = "Event already wishlisted"
                serializer = WishListSerializer(wishlist)
                return api_success_response(message=message, data=serializer.data, status=200)

            serializer = WishListSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return api_success_response(data=serializer.data, message="Wishlisted successfully",
                                        status=200)

        return api_error_response(message="Request Parameters are invalid", status=400)

    def destroy(self, request, pk=None):
        """
        Destroy api for wish list
        """
        event_id = pk
        token = get_authorization_header(request).split()[1]
        payload = jwt.decode(token, SECRET_KEY)
        user_id = payload['user_id']
        if user_id and event_id:
            try:
                instance = WishList.objects.get(event=event_id, user=user_id)
            except:
                return api_error_response(message='Not wishlisted', status=400)
            instance.is_active = False
            instance.save()
            return api_success_response(message='Successfully removed from wishlist', status=200)

        return api_error_response(message='Invalid event', status=400)
