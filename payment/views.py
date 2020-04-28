"""
Payment related views are here
"""
import datetime

from eon_backend.settings.common import APP_CONSTANTS
from payment.serializers import PaymentSerializer

CONSTANTS = APP_CONSTANTS['transaction']['values']


def event_payment(data=None):
    """
    Evnent payment method added here
    """
    card_number = data.get('card_number', None)
    expiry_month = data.get('expiry_month', None)
    expiry_year = data.get('expiry_year', None)
    amount = data.get('amount', None)
    discount_amount = data.get('discount_amount', None)
    total_amount = data.get('total_amount', )
    no_of_tickets = data.get('no_of_tickets', None)
    now = datetime.datetime.now()
    year = now.year
    month = now.month

    if not discount_amount:
        discount_amount = 0
    if not total_amount:
        if amount < 0:
            total_amount = amount*(-1) - discount_amount
            amount = amount*-1
        else:
            total_amount = amount - discount_amount

    check = False
    if no_of_tickets < 0:
        check = True
        status = 3
    else:
        if not amount or not card_number or not expiry_year or not expiry_month:
            return "Request Parameters are invalid"
        status = 0
        if isinstance(card_number, int) and len(str(card_number)) == 16 and (
                expiry_year > year or (expiry_year == year and expiry_month > month)):
            check = True
    if check:
        data = dict(amount=amount, discount_amount=discount_amount, total_amount=total_amount,
                    status=status)
        serializer = PaymentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = serializer.data
        data.pop('status')
        return data

    return "Payment Failed"
