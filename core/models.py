from django.db import models

# Create your models here.
from authentication.models import ModelBase, User


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
    status = models.ForeignKey(EventStatus, on_delete=models.DO_NOTHING,)
    external_links = models.CharField(max_length=1024)

    class Meta:
        unique_together = ("name", "type", "date", "time")

    def __str__(self):
        return "{}-{}-{}".format(self.name, self.type, self.status)


class Invitation(ModelBase):
    event = models.ForeignKey(Event, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    discount_percentage = models.PositiveIntegerField()

    def __str__(self):
        return "{}-{}-{}".format(self.event, self.user, self.discount_percentage)


class EventPreference(ModelBase):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    event_type = models.ForeignKey(EventType, on_delete=models.DO_NOTHING)

    def __str__(self):
        return "{}-{}-{}".format(self.user, self.event_type)


class Subscription(ModelBase):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    event = models.ForeignKey(Event, on_delete=models.DO_NOTHING)
    no_of_tickets = models.PositiveIntegerField()
    payment = models.ForeignKey(Payment, on_delete=models.DO_NOTHING)

    def __str__(self):
        return "{}-{}-{}".format(self.user, self.event, self.no_of_tickets)
