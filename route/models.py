from django.db import models
from django.utils.translation import gettext_lazy
# Create your models here.

class Places(models.Model):
    name = models.CharField(max_length=50)

class Route(models.Model):
    starting_point = models.IntegerField()
    stopping_point = models.JSONField()
    destination = models.IntegerField()
    country = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    description = models.TextField()
    duration = models.IntegerField()

    class RouteType(models.TextChoices):
        Car = 'Car', gettext_lazy('Car')
        Foot = 'Foot', gettext_lazy('Foot')

    route_type = models.CharField(
        max_length=10,
        choices=RouteType.choices,
        default=RouteType.Foot
    )


class Event(models.Model):
    id_route = models.IntegerField()
    event_admin = models.IntegerField()
    approved_users = models.JSONField()
    pending_users = models.JSONField()
    start_date = models.DateField()
    price = models.IntegerField()


class Review(models.Model):
    route_id = models.IntegerField()
    review_text = models.TextField()
    review_rate = models.IntegerField()
