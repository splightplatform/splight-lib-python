from django.db import models
from model_utils.managers import InheritanceManager
from splight_storage.models.geopoint import Geopoint
from splight_storage.models.tag import Tag
from splight_storage.models.tenant import TenantAwareModel


class Asset(TenantAwareModel):
    objects = InheritanceManager()
    external_id = models.CharField(max_length=100, blank=True, unique=True)
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    tags = models.ManyToManyField(Tag, blank=True)
    geopoints = models.ManyToManyField(Geopoint, blank=True)

    class Meta:
        app_label = 'splight_storage'
