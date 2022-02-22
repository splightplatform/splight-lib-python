from django.db import models
from .namespace import NamespaceAwareModel


class Geopoint(NamespaceAwareModel):
    latitude = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    longitude = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return '(' + str(self.latitude) + ',' + str(self.longitude) + ')'
