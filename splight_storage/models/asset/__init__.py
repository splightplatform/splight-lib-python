from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from pandas.core.frame import DataFrame


class Asset(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
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

    def read(self) -> DataFrame:
        if not self.connector:
            raise NotImplementedError
        return self.connector.read()

    def hist(self) -> DataFrame:
        if not self.connector:
            raise NotImplementedError
        return self.connector.hist()

    def storage(self) -> DataFrame:
        raise NotImplementedError
