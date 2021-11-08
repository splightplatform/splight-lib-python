from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from model_utils.managers import InheritanceManager
from pandas.core.frame import DataFrame
from splight_storage.models.tag import Tag
from splight_storage.models.tenant import TenantAwareModel


class Asset(TenantAwareModel):
    objects = InheritanceManager()
    external_id = models.CharField(max_length=100, blank=True, unique=True) # TODO this must not be empty
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    longitude = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    latitude = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    connector_id = models.PositiveIntegerField(blank=True, null=True)
    connector_type = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        default=None,
        on_delete=models.CASCADE,
    )
    connector = GenericForeignKey('connector_type', 'connector_id')

    class Meta:
        app_label = 'splight_storage'
