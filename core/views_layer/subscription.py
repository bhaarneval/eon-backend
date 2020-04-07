import json

from django.db import transaction
from django.db.models import F, Value, IntegerField, Sum
from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Subscription, Event
from core.serializers import SubscriptionListSerializer, SubscriptionSerializer
from payment.views import event_payment
from utils.common import api_success_response, api_error_response


class SubscriptionViewSet(viewsets.ViewSet):
    authentication_classes = (JWTAuthentication,)
    queryset = Subscription.objects.all()

    def list(self, request, *args, **kwargs):
        event_id = request.GET.get("event_id", None)
        if event_id:
            self.queryset = self.queryset.filter(event=event_id)

        self.queryset = self.queryset.select_related('user').annotate(email=F('user__email'),
                                                                      name=F('user__userprofile__name'),
                                                                      contact_number=F(
                                                                          'user__userprofile__contact_number'))

        queryset = self.queryset.filter(payment__isnull=True)
        self.queryset = self.queryset.filter(payment__isnull=False)
        self.queryset = self.queryset.select_related('payment').annotate(paid_amount=F('payment__total_amount'))
        queryset = queryset.select_related('payment').annotate(paid_amount=Value(0, IntegerField()))
        queryset = self.queryset.union(queryset)
        serializer = SubscriptionListSerializer(queryset, many=True)
        data = dict(total=len(queryset), subscribtion_list=serializer.data)
        return api_success_response(data=data, status=200)

    @transaction.atomic()
    def create(self, request):
        """
            Function to set subscription of a user to a particular event
            :param request: token, event_id, no_of_tickets, user_id, card_number, expiry_month, expiry_year,
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

        if not event_id or not no_of_tickets or not user_id:
            return api_error_response(message="Request Parameters are invalid")
        if no_of_tickets < 0:
            instance = Subscription.objects.filter(user=user_id, event=event_id)
            tickets_data = instance.values('event').annotate(total_tickets=Sum('no_of_tickets')).first()
            remianing_tickets = no_of_tickets + tickets_data['total_tickets']
            if remianing_tickets < 0:
                return api_error_response(message="Number of tickets are invalid", status=400)

        if amount:
            data = dict(card_number=card_number, expiry_month=expiry_month, expiry_year=expiry_year, amount=amount,
                        discount_amount=discount_amount, total_amount=total_amount, no_of_tickets=no_of_tickets)

            payment_object = event_payment(data)

            if isinstance(payment_object, str):
                return api_error_response(message=payment_object, status=400)

            payment_id = payment_object['id']

        data = dict(user=user_id, event=event_id, no_of_tickets=no_of_tickets, payment=payment_id)

        try:
            self.event = Event.objects.get(id=event_id)
        except:
            return api_error_response("Invalid event_id")

        if not payment_id and self.event.subscription_fee > 0:
            return api_error_response(message="Required Fields are not present")

        if self.event.no_of_tickets - self.event.sold_tickets >= no_of_tickets:
            serializer = SubscriptionSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            if serializer.instance.payment:
                queryset = Subscription.objects.filter(user=user_id, event=event_id, payment__isnull=False,
                                                       payment__status=0)
                queryset1 = Subscription.objects.filter(user=user_id, event=event_id, payment__isnull=False,
                                                        payment__status=3)

                queryset = queryset.select_related('payment')
                queryset = queryset.select_related('event')
                queryset1 = queryset1.select_related('payment')
                queryset1 = queryset1.select_related('event')
                queryset = queryset.values('event').annotate(amount=F('payment__amount'),
                                                             discount_amount=F('payment__discount_amount'),
                                                             total_amount=F('payment__total_amount'),
                                                             events=F('event'), event_name=F('event__name'),
                                                             event_date=F('event__date'), event_time=F('event__time'),
                                                             event_location=F('event__location'))
                queryset1 = queryset1.values('event').annotate(amount=F('payment__amount'),
                                                               discount_amount=F('payment__discount_amount'),
                                                               total_amount=F('payment__total_amount'))
                data = queryset.aggregate(Sum('amount'), Sum('discount_amount'), Sum('total_amount'),
                                          Sum('no_of_tickets'))
                data1 = queryset1.aggregate(Sum('amount'), Sum('discount_amount'), Sum('total_amount'),
                                            Sum('no_of_tickets'))
                queryset = queryset.first()
                data = dict(no_of_tickets=data['no_of_tickets__sum'] + data1['no_of_tickets__sum'],
                            amount=data['amount__sum'] - data1['amount__sum'],
                            discount_amount=data['discount_amount__sum'] - data1['discount_amount__sum'],
                            total_amount=data['total_amount__sum'] - data1['total_amount__sum'],
                            event_name=queryset['event_name'],
                            event_date=queryset['event_date'], event_time=queryset['event_time'],
                            event_location=queryset['event_location'])

            return api_success_response(message="Subscribed Successfully", data=data, status=201)
        else:
            return api_error_response(message="Number of tickets are invalid", status=400)

