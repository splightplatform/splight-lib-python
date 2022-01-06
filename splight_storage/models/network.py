from django.db import models
from splight_storage.models.tenant import TenantAwareModel


def upload_to(instance, filename):
    # file will be uploaded to MEDIA_ROOT/Network/<tenant.org_id>/<filename>
    return 'Network/{0}/{1}'.format(instance.tenant.org_id, filename)


class Network(TenantAwareModel):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=10, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    file = models.FileField(blank=True, null=True, upload_to=upload_to)

    class Meta:
        app_label = 'splight_storage'
        ordering = ['-id']

    def __str__(self):
        return f"{self.name if self.name else self.id}"
