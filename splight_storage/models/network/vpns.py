from django.db import models
from . import Network


def upload_to(instance, filename):
    # file will be uploaded to MEDIA_ROOT/OpenVPNNetwork/<tenant.org_id>/<filename>
    return 'OpenVPNNetwork/{0}/{1}'.format(instance.tenant.org_id, filename)


class OpenVPNNetwork(Network):
    username = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)

    file = models.FileField(blank=True, null=True, upload_to=upload_to)
