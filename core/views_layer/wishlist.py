import json

import jwt
from django.db import transaction
from django.db.models import F
from rest_framework import viewsets
from rest_framework.authentication import get_authorization_header
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import WishList
from core.serializers import WishListSerializer
from eon_backend.settings import SECRET_KEY
from utils.common import api_error_response, api_success_response


class WishListViewSet(viewsets.ViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )
    queryset = WishList.objects.filter(is_active=True)

    @transaction.atomic()
    def create(self, request):
        data = json.loads(request.body)
        event_id = data.get('event_id', None)
        token = get_authorization_header(request).split()[1]
        payload = jwt.decode(token, SECRET_KEY)
        user_id = payload['user_id']

        if user_id and event_id:
            data = [dict(user=user_id, event=event_id)]
            serializer = WishListSerializer(data=data, many=True)
            serializer.is_valid()
            if 'non_field_errors' in serializer.errors[0]:
                queryset = WishList.objects.filter(user=user_id, event=event_id)
                queryset = queryset.select_related('user', 'event').annotate(event_name=F('event__name'), user_name=F('user__userprofile__name'))
                queryset = queryset.first()
                data = dict(id=queryset.id, user=queryset.user_name, event=queryset.event_name)
                if queryset.is_active:
                    message = "Event already wishlisted"
                else:
                    queryset.is_active = True
                    queryset.save()
                    message = "WishListed Successfully"
                return api_success_response(message=message, data=data,  status=200)
            elif serializer.errors:
                return api_error_response(message="Event Invalid", status=400)
            serializer.save()
            queryset = WishList.objects.filter(user=user_id, event=event_id)
            queryset = queryset.select_related('user', 'event').annotate(event_name=F('event__name'),
                                                                         user_name=F('user__userprofile__name'))
            queryset = queryset.first()
            data = dict(id=queryset.id, user=queryset.user_name, event=queryset.event_name)
        return api_success_response(data=data, message="WishListed Successfully", status=200)

    def destroy(self, request, pk=None):
        event_id = pk
        token = get_authorization_header(request).split()[1]
        payload = jwt.decode(token, SECRET_KEY)
        user_id = payload['user_id']
        if user_id and event_id:
            try:
                instance = WishList.objects.get(event=event_id, user=user_id)
            except:
                return api_error_response(message='Not WishListed', status=400)
            instance.is_active = False
            instance.save()
            return api_success_response(message='Successfully removed from Wishlist', status=200)
        else:
            return api_error_response(message='Invalid event', status=400)
