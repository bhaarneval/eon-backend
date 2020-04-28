"""
All subscription related api are here
"""
import json
import requests
import jwt
from django.db import transaction
from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from rest_framework import viewsets
from rest_framework.authentication import get_authorization_header
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Subscription, Event
from core.serializers import SubscriptionSerializer
from eon_backend.settings import SECRET_KEY
from utils.common import api_success_response, api_error_response
from utils.constants import PAYMENT_URL
from utils.permission import IsSubscriberOrReadOnly


class SubscriptionViewSet(viewsets.ViewSet):
    """
    Api methods for subscriptions added here
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, IsSubscriberOrReadOnly)
    queryset = Subscription.objects.filter(is_active=True)

    @transaction.atomic()
    def create(self, request):
        """
            Function to set subscription of a user to a particular event
            :param request: token, event_id, no_of_tickets,
            user_id, card_number, expiry_month, expiry_year,
                            amount, discount_amount, total_amount
            :return: json response subscribed successful or error message
        """
        data = json.loads(request.body)
        event_id = data.get('event_id', None)
        no_of_tickets = data.get('no_of_tickets', None)
        user_id = data.get('user_id', None)
        card_number = data.get('card_number', None)
        expiry_month = data.get('expiry_month', None)
        expiry_year = data.get('expiry_year', None)
        amount = data.get('amount', None)
        discount_amount = data.get('discount_amount', None)
        total_amount = data.get('total_amount', None)
        payment_id = None

        token = get_authorization_header(request).split()[1]
        payload = jwt.decode(token, SECRET_KEY)
        user_id = payload['user_id']

        if not event_id or not no_of_tickets or not user_id:
            return api_error_response(message="Request parameters are invalid")

        try:
            self.event = Event.objects.get(id=event_id, is_active=True)
        except Event.DoesNotExist:
            return api_error_response("Invalid event id")

        if no_of_tickets < 0:
            instance = self.queryset.filter(user=user_id, event=event_id)
            tickets_data = instance.values('event').aggregate(Sum('no_of_tickets'))
            remaining_tickets = no_of_tickets + tickets_data['no_of_tickets__sum']
            if remaining_tickets < 0:
                return api_error_response(message="Can not cancel tickets more than purchase", status=400)

        if amount:
            data = dict(card_number=card_number, expiry_month=expiry_month,
                        expiry_year=expiry_year, amount=amount,
                        discount_amount=discount_amount, total_amount=total_amount,
                        no_of_tickets=no_of_tickets)

            payment_object = requests.post(PAYMENT_URL, data=json.dumps(data),
                                           headers={"Authorization": f"Bearer {token.decode('utf-8')}",
                                                    "Content-type": "application/json"})
            if payment_object.status_code == 200:
                payment_object = payment_object.json().get('data')
                if payment_object['status'] == 3:
                    payment_object['total_amount'] = payment_object['total_amount'] * (-1)

            else:
                return api_error_response(message="Error while fetching payment", status=500)

            payment_id = payment_object['id']
            amount = payment_object['total_amount']

        data = dict(user=user_id, event=event_id, no_of_tickets=no_of_tickets, id_payment=payment_id, amount=amount)

        if not payment_id and self.event.subscription_fee > 0:
            return api_error_response(message="Required fields are not present")

        if self.event.no_of_tickets - self.event.sold_tickets >= no_of_tickets:
            serializer = SubscriptionSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            if serializer.instance.id_payment:
                success_queryset = self.queryset.filter(user=user_id, event=event_id,
                                                        id_payment__isnull=False,
                                                        amount__gt=0)
                refund_queryset = self.queryset.filter(user=user_id, event=event_id,
                                                       id_payment__isnull=False,
                                                       amount__lt=0)

                success_queryset = success_queryset.select_related('event')
                refund_queryset = refund_queryset.select_related('event')
                success_queryset = success_queryset.values('event').annotate(
                    total_amount=Coalesce(Sum('amount'), 0),
                    total_tickets=Coalesce(Sum('no_of_tickets'), 0),
                    event_name=F('event__name'),
                    event_date=F('event__date'),
                    event_time=F('event__time'),
                    event_location=F('event__location'))
                refund_queryset = refund_queryset.values('event').annotate(
                    total_amount=Coalesce(Sum('amount'), 0),
                    total_tickets=Coalesce(Sum('no_of_tickets'), 0))

                if len(success_queryset) > 0:
                    success_queryset = success_queryset[0]
                if len(refund_queryset) > 0:
                    refund_queryset = refund_queryset[0]
                    refund_total_amount = refund_queryset['total_amount']
                    refund_total_tickets = refund_queryset['total_tickets']
                else:
                    refund_total_amount = 0
                    refund_total_tickets = 0
                data = dict(curent_payment_id=payment_id,
                            no_of_tickets=
                            int(success_queryset['total_tickets'] + refund_total_tickets),
                            total_amount=success_queryset['total_amount'] + refund_total_amount,
                            event_name=success_queryset['event_name'],
                            event_date=success_queryset['event_date'],
                            event_time=success_queryset['event_time'],
                            event_location=success_queryset['event_location'])
            else:
                queryset = self.queryset.filter(event=event_id, user=user_id, id_payment=None)
                queryset = queryset.select_related('event')
                tickets_data = queryset.aggregate(Sum('no_of_tickets'))
                queryset = queryset.values('event').annotate(
                    event_name=F('event__name'),
                    event_date=F('event__date'),
                    event_time=F('event__time'),
                    event_location=F('event__location'))
                queryset = queryset.first()
                data = dict(
                    no_of_tickets=int(tickets_data['no_of_tickets__sum']),
                    event_name=queryset['event_name'],
                    event_date=queryset['event_date'], event_time=queryset['event_time'],
                    event_location=queryset['event_location'])

            return api_success_response(message="Subscribed successfully", data=data, status=201)

        return api_error_response(message="Requested number of tickets are more than available", status=400)

    def destroy(self, request, pk=None):
        """
        Function to unsubscribe subscription of a user to a particular event
            :return: json response Successfully Unsubscribed
        """
        event_id = pk
        token = get_authorization_header(request).split()[1]
        payload = jwt.decode(token, SECRET_KEY)
        user_id = payload['user_id']
        event_to_be_added_to_inactive = self.queryset.filter(user_id=user_id, event_id=event_id)
        total_tickets = event_to_be_added_to_inactive.aggregate(Sum('no_of_tickets'))
        event = Event.objects.get(id=event_id)
        event.sold_tickets -= total_tickets['no_of_tickets__sum']
        event.save()
        event_to_be_added_to_inactive.update(is_active=False)
        return api_success_response(message="Successfully unsubscribed")
