from django.db import models
from model_utils.managers import InheritanceManager
from splight_storage.models.tenant import TenantAwareModel
from splight_storage.models.network import Network


class Connector(TenantAwareModel):

    class Protocols(models.TextChoices):
        DNP3 = 'dnp3', "DNP3"
        IEC61850 = 'iec6', "IEC61850"

    objects = InheritanceManager()
    ip = models.CharField(max_length=60)
    port = models.IntegerField()
    protocol = models.CharField(max_length=4, choices=Protocols.choices)

    def __repr__ (self):
        return '<Connector %s>' % self.__str__

    def __str__ (self):
        return '%s:%s[%s]' % (self.ip, self.port, self.protocol)


class ServerConnector(Connector):
    network = models.ForeignKey(Network, related_name="server_connectors", on_delete=models.CASCADE, null=True, blank=True)


class ClientConnector(Connector):
    network = models.ForeignKey(Network, related_name="client_connectors", on_delete=models.CASCADE, null=True, blank=True)
