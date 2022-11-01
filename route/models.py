import datetime

from django.db import models
from django.utils.translation import gettext_lazy
import json
from django.core.exceptions import ValidationError


# Create your models here.


def validate_stopping_point(value):
    try:
        stopping = json.loads(value)
        for itm in stopping:
            if 'name' in itm and 'lat' in itm and 'lon' in itm:
                continue
            else:
                raise ValueError("Error")
    except:
        raise ValueError("Some data is not included")


def validate_route_type(value):
    if value.title() not in ['Car', 'Foot']:
        raise ValueError("Error")


def validate_date(value):
    try:
        parsed_date = datetime.datetime.strptime(str(value), "%Y-%m-%d")
    except:
        raise ValueError("Date Error")
    if datetime.datetime.today() > parsed_date:
        raise ValueError("Date Error")


class Places(models.Model):
    name = models.CharField(max_length=50)


class Route(models.Model):
    starting_point = models.IntegerField()
    stopping_point = models.CharField(max_length=50)
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
        default=RouteType.Foot,
        validators=[validate_route_type]
    )


class Event(models.Model):
    id_route = models.IntegerField()
    event_admin = models.IntegerField()
    event_users = models.CharField(max_length=50, null=True)
    start_date = models.DateField(validators=[validate_date])
    price = models.IntegerField()


class Review(models.Model):
    route_id = models.IntegerField()
    review_text = models.TextField()
    review_rate = models.IntegerField()
