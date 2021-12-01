from django.db import models
from model_utils.managers import InheritanceManager
from splight_storage.models.tenant import TenantAwareModel
from splight_storage.models.network import Network


class Connector(TenantAwareModel):

    class Protocols(models.TextChoices):
        DNP3 = 'dnp3', "DNP3"
        IEC61850 = 'iec6', "IEC61850"

    objects = InheritanceManager()
    ip = models.GenericIPAddressField()
    port = models.IntegerField()
    protocol = models.CharField(max_length=4, choices=Protocols.choices)


class ServerConnector(Connector):
    network = models.ForeignKey(Network, related_name="server_connectors", on_delete=models.CASCADE)


class ClientConnector(Connector):
    network = models.ForeignKey(Network, related_name="client_connectors", on_delete=models.CASCADE)
