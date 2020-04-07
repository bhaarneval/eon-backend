from rest_framework import serializers

from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ('id', 'amount', 'discount_amount', 'total_amount', 'ref_number', 'status')
