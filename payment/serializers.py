"""
Serializers for payment models
"""
from rest_framework import serializers

from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """
    Add your comment here about this class
    """

    class Meta:
        """
        To override the database table name, use the db_table parameter in class Meta.
        """
        model = Payment
        fields = ('id', 'amount', 'discount_amount', 'total_amount', 'ref_number', 'status')
