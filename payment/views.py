import datetime
import json

from django.conf import settings
from rest_framework import mixins, generics
from rest_framework_simplejwt.authentication import JWTAuthentication

from payment.models import Payment
from payment.serializers import PaymentSerializer
from utils.common import api_error_response, api_success_response


class PaymentViewSet(mixins.CreateModelMixin, generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    queryset = Payment.objects.all()

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        card_number = data.get('card_number', None)
        expiry_month = data.get('expiry_month', None)
        expiry_year = data.get('expiry_year', None)
        amount = data.get('amount', None)
        discount_amount = data.get('discount_amount', None)
        total_amount = data.get('total_amount', None)
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        if not amount or not discount_amount or not card_number or not expiry_year or not expiry_month:
            return api_error_response(message="Request Parameters are invalid", status=400)
        if not total_amount:
            total_amount = amount - discount_amount

        if isinstance(card_number, int) and len(str(card_number)) == 16 and (
                expiry_year > year or (expiry_year == year and expiry_month > month)):

            data = dict(amount=amount, discount_amount=discount_amount,
                        total_amount=total_amount)

            serializer = PaymentSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return api_success_response(message="Payment successfully Done.", status=200)
        else:
            return api_error_response(message="Payment Failed", status=400)
