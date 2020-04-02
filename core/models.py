from django.db import models

# Create your models here.


class EventStatus(models.Model):
    type = models.CharField(unique=True, max_length=256)

    class Meta:
        verbose_name_plural = "Event Status"

    def __str__(self):
        return self.type


class EventType(models.Model):
    type = models.CharField(unique=True, max_length=256)

    def __str__(self):
        return self.type


class Promotion(models.Model):
    discount_percentage = models.PositiveIntegerField()
    channel = models.CharField(max_length=256)

    def __str__(self):
        return "{}-{}".format(self.discount_percentage, self.channel)


class Event(models.Model):
    name = models.CharField(max_length=256)
    type = models.ForeignKey(EventType, on_delete=models.DO_NOTHING)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=512)
    images = models.URLField()
    subscription_fee = models.PositiveIntegerField()
    no_of_tickets = models.PositiveIntegerField()
    status = models.ForeignKey(EventStatus, on_delete=models.DO_NOTHING)
    promotion = models.ForeignKey(Promotion, on_delete=models.DO_NOTHING, null=True)

    class Meta:
        unique_together = ("name", "type", "date", "time")

    def __str__(self):
        return "{}-{}-{}".format(self.name, self.type, self.status)
