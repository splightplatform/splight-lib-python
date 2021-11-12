from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from model_utils.managers import InheritanceManager
from pandas.core.frame import DataFrame
from splight_storage.models.geopoint import Geopoint
from splight_storage.models.tag import Tag
from splight_storage.models.tenant import TenantAwareModel


class Asset(TenantAwareModel):
    id = models.BigAutoField(primary_key=True)
    objects = InheritanceManager()
    # TODO this must not be empty
    external_id = models.CharField(max_length=100, blank=True, unique=True)

    name = models.CharField(max_length=100)
    status = models.IntegerField(default=1)

    tags = models.ManyToManyField(Tag, blank=True)
    geopoints = models.ManyToManyField(Geopoint, blank=True)
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
