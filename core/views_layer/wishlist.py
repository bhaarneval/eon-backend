import json

import jwt
from django.db import transaction
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
        user_id = data.get('user_id', None)

        if user_id and event_id:
            data = dict(user=user_id, event=event_id)
            try:
                serializer = WishListSerializer(data=data)
            except:
                return api_error_response(message="Invalid Event", status=400)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return api_success_response(data=serializer.data, message="WishListed Successfully", status=200)

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
            return api_success_response(message='Successfully Unsubscribed', status=200)
        else:
            return api_error_response(message='Invalid event', status=400)
