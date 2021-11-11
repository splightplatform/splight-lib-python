from django.db import models
from splight_storage.models.tenant import TenantAwareModel


class Geopoint(TenantAwareModel):
    latitude = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    longitude = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)

    @property
    def status(self):
        return 1

    def __str__(self):
        return '(' + str(self.latitude) + ',' + str(self.longitude) + ')'
