from django.db import models
from . import Network


class OpenVPNNetwork(Network):
    username = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)

    file = models.FileField(blank=True, null=True)
