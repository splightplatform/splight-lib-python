from django.db import models


class Tenant(models.Model):
    org_id = models.CharField(max_length=100)
    # subdomain_prefix = models.CharField(max_length=100, unique=True)


class TenantAwareModel(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, default=None, null=True, blank=True)

    class Meta:
        abstract = True