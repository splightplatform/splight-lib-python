from django.db import models
from splight_storage.models.tenant import TenantAwareModel


class Attribute(TenantAwareModel):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if Attribute.objects.filter(name=self.name, tenant=self.tenant):
            # TODO raise typed exception
            raise Exception
        super(Attribute, self).save(*args, **kwargs)
