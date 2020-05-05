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
from eon_backend.settings.common import SECRET_KEY, LOGGER_SERVICE
from utils.common import api_error_response, api_success_response
from utils.permission import IsSubscriberOrReadOnly

logger = LOGGER_SERVICE


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
        logger.log_info("Wishlist creation started")
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
                logger.log_error(f"Invalid Event with id {event_id}")
                return api_error_response(message="Invalid Event", status=400)

            if event and event.event_created_by == user_id:
                logger.log_error("LoggedIn user is not organizer of event")
                return api_error_response(message="You are the Organizer of the event", status=400)

            try:
                wishlist = WishList.objects.get(user=user_id, event=event_id)
            except:
                pass
            if wishlist:
                if not wishlist.is_active:
                    wishlist.is_active = True
                    wishlist.save()
                    message = "Wishlisted successfully"
                else:
                    message = "Event already wishlisted"
                serializer = WishListSerializer(wishlist)
                return api_success_response(message=message, data=serializer.data, status=200)

            serializer = WishListSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            logger.log_info(
                f"Wishlist successfully added for user_id {user_id} for event {event_id}")
            return api_success_response(data=serializer.data, message="Wishlisted successfully",
                                        status=200)
        logger.log_error("Request Parameters are invalid")
        return api_error_response(message="Request Parameters are invalid", status=400)

    def destroy(self, request, pk=None):
        """
        Destroy api for wish list
        """
        logger.log_info("Wishlist remove process started")
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
            logger.log_info(f"Wishlist removed successfully for user_id {user_id}")
            return api_success_response(message='Successfully removed from wishlist', status=200)

        logger.log_error(f"Invalid event {event_id}")
        return api_error_response(message='Invalid event', status=400)
