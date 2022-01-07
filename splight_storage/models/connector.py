from django.db import models
from typing import Dict
from model_utils.managers import InheritanceManager
from splight_storage.models.tenant import TenantAwareModel
from splight_storage.models.network import Network


class Protocol(models.TextChoices):
    DNP3 = 'dnp3', "DNP3"
    IEC61850 = 'iec6', "IEC61850"


class Connector(TenantAwareModel):
    objects = InheritanceManager()
    host = models.CharField(max_length=60)
    port = models.IntegerField()
    protocol = models.CharField(max_length=4, choices=Protocol.choices)
    extra_properties = models.TextField(null=True, blank=True)

    def __repr__ (self):
        return '<Connector %s>' % self.__str__

    def __str__ (self):
        return '%s:%s[%s]' % (self.host, self.port, self.protocol)

    @property
    def extra_env(self) -> Dict:
        variables = [var.split("=") for var in self.extra_properties.splitlines()]
        valid_variables = [var for var in variables if len(var) == 2]
        return {str(key): value for key, value in valid_variables}


class ServerConnector(Connector):
    network = models.ForeignKey(Network, related_name="server_connectors", on_delete=models.CASCADE, null=True, blank=True)
    external_port = models.IntegerField()

    class Meta:
        unique_together = ("network", "external_port",)


class ClientConnector(Connector):
    network = models.ForeignKey(Network, related_name="client_connectors", on_delete=models.CASCADE, null=True, blank=True)
