from django.db import models

# Create your models here.
from authentication.models import ModelBase


class EventStatus(ModelBase):
    type = models.CharField(unique=True, max_length=256)

    class Meta:
        verbose_name_plural = "Event Status"

    def __str__(self):
        return self.type


class EventType(ModelBase):
    type = models.CharField(unique=True, max_length=256)

    def __str__(self):
        return self.type


class Promotion(ModelBase):
    name = models.CharField(max_length=48)
    discount_percentage = models.PositiveIntegerField()
    channel = models.CharField(max_length=20)

    def __str__(self):
        return "{}-{}".format(self.discount_percentage, self.channel)


class Event(ModelBase):
    name = models.CharField(max_length=256)
    type = models.ForeignKey(EventType, on_delete=models.DO_NOTHING)
    description = models.CharField(max_length=512)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=512)
    images = models.URLField()
    subscription_fee = models.PositiveIntegerField()
    no_of_tickets = models.PositiveIntegerField()
    status = models.ForeignKey(EventStatus, on_delete=models.DO_NOTHING)
    promotion = models.ForeignKey(Promotion, on_delete=models.DO_NOTHING, null=True)
    external_links = models.CharField(max_length=1024)

    class Meta:
        unique_together = ("name", "type", "date", "time")

    def __str__(self):
        return "{}-{}-{}".format(self.name, self.type, self.status)
