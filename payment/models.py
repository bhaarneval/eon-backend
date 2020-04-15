"""
Payment related model created here
"""
import uuid
from django.conf import settings
from django.db import models

# Create your models here.
from authentication.models import ModelBase

PAYMENT_CONSTANTS = settings.APP_CONSTANTS["transaction"]
PAYMENT_STATUS = PAYMENT_CONSTANTS['status']


class Payment(ModelBase):
    """
    Payment model created here
    """
    amount = models.PositiveIntegerField()
    discount_amount = models.PositiveIntegerField()
    total_amount = models.PositiveIntegerField()
    ref_number = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.PositiveSmallIntegerField(choices=PAYMENT_CONSTANTS["status"], default=0)

    def __str__(self):
        amount = "{}".format(self.total_amount)
        if self.status == 0:
            status = " (CREDIT)"
        else:
            status = " ({})".format(PAYMENT_STATUS[self.status][1])
        return amount + status
