from django.db import models
from .namespace import NamespaceAwareModel


def upload_to(instance, filename):
    # file will be uploaded to MEDIA_ROOT/Network/<namespace.namespace>/<filename>
    return 'Network/{0}/{1}'.format(instance.namespace.id, filename)


class Network(NamespaceAwareModel):
    name = models.CharField(max_length=10, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    file_id = models.CharField(max_length=100, null=True, blank=True)
