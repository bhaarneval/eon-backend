"""
All subscription related api are here
"""
import json

import jwt
from django.db import transaction
from django.db.models import F, Value, IntegerField, Sum
from django.db.models.functions import Coalesce
from rest_framework import viewsets
from rest_framework.authentication import get_authorization_header
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Subscription, Event
from core.serializers import SubscriptionListSerializer, SubscriptionSerializer
from eon_backend.settings import SECRET_KEY, LOGGER_SERVICE
from payment.views import event_payment
from utils.common import api_success_response, api_error_response
from utils.permission import IsSubscriberOrReadOnly

logger = LOGGER_SERVICE


class SubscriptionViewSet(viewsets.ViewSet):
    """
    Api methods for subscriptions added here
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, IsSubscriberOrReadOnly)
    queryset = Subscription.objects.filter(is_active=True)

    def list(self, request, *args, **kwargs):
        """
        Subscription List api
        """
        event_id = request.GET.get("event_id", None)
        if event_id:
            self.queryset = self.queryset.filter(event=event_id)

        self.queryset = self.queryset.select_related('user').annotate(
            email=F('user__email'),
            name=F('user__userprofile__name'),
            contact_number=F('user__userprofile__contact_number'))

        queryset = self.queryset.filter(payment__isnull=True)
        self.queryset = self.queryset.filter(payment__isnull=False)
        self.queryset = self.queryset.select_related('payment').annotate(
            paid_amount=F('payment__total_amount'))
        queryset = queryset.select_related('payment').annotate(paid_amount=Value(0, IntegerField()))
        queryset = self.queryset.union(queryset)
        serializer = SubscriptionListSerializer(queryset, many=True)
        data = dict(total=len(queryset), subscribtion_list=serializer.data)
        logger.log_info("Subscription list fetched successfully")
        return api_success_response(data=data, status=200)

    @transaction.atomic()
    def create(self, request):
        """
            Function to set subscription of a user to a particular event
            :param request: token, event_id, no_of_tickets,
            user_id, card_number, expiry_month, expiry_year,
                            amount, discount_amount, total_amount
            :return: json response subscribed successful or error message
        """
        logger.log_info("Subscription Started")
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

        if not event_id or not no_of_tickets or not user_id:
            logger.log_error("Event_id, no_of_tickets and user_id are mandatory in request")
            return api_error_response(message="Request Parameters are invalid")

        try:
            self.event = Event.objects.get(id=event_id, is_active=True)
        except Event.DoesNotExist:
            logger.log_error(f"Event_id {event_id} does not exist")
            return api_error_response("Invalid event_id")

        if no_of_tickets < 0:
            instance = self.queryset.filter(user=user_id, event=event_id)
            tickets_data = instance.values('event').aggregate(Sum('no_of_tickets'))
            remaining_tickets = no_of_tickets + tickets_data['no_of_tickets__sum']
            if remaining_tickets < 0:
                logger.log_error(f"Invalid number of tickets entered {no_of_tickets}")
                return api_error_response(message="Number of tickets are invalid", status=400)

        if amount:
            data = dict(card_number=card_number, expiry_month=expiry_month,
                        expiry_year=expiry_year, amount=amount,
                        discount_amount=discount_amount, total_amount=total_amount,
                        no_of_tickets=no_of_tickets)

            payment_object = event_payment(data)

            if isinstance(payment_object, str):
                return api_error_response(message=payment_object, status=400)

            payment_id = payment_object['id']

        data = dict(user=user_id, event=event_id, no_of_tickets=no_of_tickets, payment=payment_id)

        if not payment_id and self.event.subscription_fee > 0:
            return api_error_response(message="Required Fields are not present")

        if self.event.no_of_tickets - self.event.sold_tickets >= no_of_tickets:
            serializer = SubscriptionSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            if serializer.instance.payment:
                current_payment_queryset = self.queryset.filter(event=event_id, payment=payment_id)
                current_payment_queryset = current_payment_queryset.select_related('payment')
                current_payment_queryset = current_payment_queryset.annotate(
                    ref_no=F('payment__ref_number'))
                success_queryset = self.queryset.filter(user=user_id, event=event_id,
                                                        payment__isnull=False,
                                                        payment__status=0)
                refund_queryset = self.queryset.filter(user=user_id, event=event_id,
                                                       payment__isnull=False,
                                                       payment__status=3)

                success_queryset = success_queryset.select_related('payment')
                success_queryset = success_queryset.select_related('event')
                refund_queryset = refund_queryset.select_related('payment')
                refund_queryset = refund_queryset.select_related('event')
                success_queryset = success_queryset.values('event').annotate(
                    amount=F('payment__amount'),
                    discount_amount=F('payment__discount_amount'),
                    total_amount=F('payment__total_amount'),
                    events=F('event'),
                    event_name=F('event__name'),
                    event_date=F('event__date'),
                    event_time=F('event__time'),
                    event_location=F('event__location'))
                refund_queryset = refund_queryset.values('event').annotate(
                    amount=F('payment__amount'),
                    discount_amount=F('payment__discount_amount'),
                    total_amount=F('payment__total_amount'))
                success_data = success_queryset.aggregate(
                    Sum('amount'), Sum('discount_amount'), Sum('total_amount'), Sum('no_of_tickets'))
                refund_data = refund_queryset.aggregate(amount__sum=Coalesce(Sum('amount'), 0),
                                                        discount_amount__sum=
                                                        Coalesce(Sum('discount_amount'), 0),
                                                        total_amount__sum=
                                                        Coalesce(Sum('total_amount'), 0),
                                                        no_of_tickets__sum=
                                                        Coalesce(Sum('no_of_tickets'), 0))
                success_queryset = success_queryset.first()
                data = dict(curent_payment_id=payment_id,
                            current_payment_ref_number=current_payment_queryset[0].ref_no,
                            no_of_tickets=
                            int(success_data['no_of_tickets__sum'] + refund_data['no_of_tickets__sum']),
                            amount=success_data['amount__sum'] - refund_data['amount__sum'],
                            discount_amount=
                            success_data['discount_amount__sum'] - refund_data['discount_amount__sum'],
                            total_amount=
                            success_data['total_amount__sum'] - refund_data['total_amount__sum'],
                            event_name=success_queryset['event_name'],
                            event_date=success_queryset['event_date'],
                            event_time=success_queryset['event_time'],
                            event_location=success_queryset['event_location'])
            else:
                queryset = self.queryset.filter(event=event_id, user=user_id, payment_id=None)
                queryset = queryset.select_related('payment')
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

            logger.log_info(f"Subscription successful for user with id {user_id}")
            return api_success_response(message="Subscribed Successfully", data=data, status=201)

        logger.log_error(f"Number of tickets are invalid for subscription request of user_id {user_id}")
        return api_error_response(message="Number of tickets are invalid", status=400)

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
        logger.log_info(f"Successfully unsubscribed event {event_id} for user_id {user_id}")
        return api_success_response(message="Successfully Unsubscribed")
