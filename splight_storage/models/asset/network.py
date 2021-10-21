from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Network(models.Model):
    name = models.CharField(max_length=50)


class NetworkRelation(models.Model):
    asset_id = models.PositiveIntegerField(blank=True, null=True)
    asset_type = models.ForeignKey(
        ContentType,
        blank=False,
        null=False,
        default=None,
        on_delete=models.CASCADE,
    )
    asset = GenericForeignKey('asset_type', 'asset_id')
    network = models.ForeignKey(
        Network,
        blank=True,
        null=True,
        default=None,
        on_delete=models.CASCADE,
    )
