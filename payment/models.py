from django.db import models

# Create your models here.
from authentication.models import ModelBase
from utils.constants import PAYMENT_CONSTANTS


class PaymentType(ModelBase):
    type = models.CharField(max_length=64)

    def __str__(self):
        return self.type


class Payment(ModelBase):
    type = models.ForeignKey(PaymentType, on_delete=models.DO_NOTHING)
    amount = models.PositiveIntegerField()
    discount = models.PositiveIntegerField()
    total_amount = models.PositiveIntegerField()
    status = models.PositiveSmallIntegerField(choices=PAYMENT_CONSTANTS["status"])

    def __str__(self):
        return "{}-{}-{}-{}".format(self.type, self.amount, self.discount, self.status)