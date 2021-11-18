from django.db import models
from . import Asset
from .devices import LineAsset


class DonutSensorAsset(Asset):
    line = models.ForeignKey(
        LineAsset, related_name='donuts', on_delete=models.CASCADE)
    angle = models.DecimalField(max_digits=4, decimal_places=2)
    orientation = models.CharField(max_length=100)
