import uuid
from django.conf import settings
from django.db import models

# Create your models here.
from authentication.models import ModelBase

PAYMENT_CONSTANTS = settings.APP_CONSTANTS["transaction"]


class Payment(ModelBase):
    amount = models.PositiveIntegerField()
    discount_amount = models.PositiveIntegerField()
    total_amount = models.PositiveIntegerField()
    ref_number = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.PositiveSmallIntegerField(choices=PAYMENT_CONSTANTS["status"], default=0)

    def __str__(self):
        return "{}-{}-{}".format(self.amount, self.discount_amount, self.status)
