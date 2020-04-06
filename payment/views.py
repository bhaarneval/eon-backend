import json

from django.conf import settings
from rest_framework import mixins, generics
from rest_framework_simplejwt.authentication import JWTAuthentication

from payment.models import Payment
from payment.serializers import PaymentSerializer
from utils.common import api_error_response, api_success_response

PAYMENT_CONSTANTS = settings.APP_CONSTANTS["transaction"]
PAYMENT_VALUES = PAYMENT_CONSTANTS['values']


class PaymentViewSet(mixins.CreateModelMixin, generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    queryset = Payment.objects.all()

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        const_type = data.get('type', None)
        amount = data.get('amount', None)
        discount_amount = data.get('discount_amount', None)
        total_amount = data.get('total_amount', None)

        if not const_type and not amount and not discount_amount:
            return api_error_response(message="Request Parameters are invalid", status=400)
        if not total_amount:
            total_amount = amount - discount_amount

        data = dict(type=PAYMENT_VALUES['type'][const_type], amount=amount, discount_amount=discount_amount,
                    total_amount=total_amount)

        serializer = PaymentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return api_success_response(message="Payment successfully Done.", status=200)
