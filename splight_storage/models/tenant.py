from django.db import models


class CrossTenantTryException(Exception):
    def __init__(self, conflicts, *args, **kwargs) -> None:
        self.conflicts = conflicts
        super().__init__(*args, **kwargs)


class Tenant(models.Model):
    org_id = models.CharField(max_length=100)
    # subdomain_prefix = models.CharField(max_length=100, unique=True)


class TenantAwareModel(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, default=None, null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Check consistency between TenantAwareModels
        nested_foreign_key = [
            field for field in self._meta.local_fields
            if type(field) == models.ForeignKey
        ]
        tenant_foreign_keys = [
            field for field in nested_foreign_key
            if isinstance(getattr(self, field.name), TenantAwareModel)
        ]
        conflicts = [
            field for field in tenant_foreign_keys
            if getattr(self, field.name).tenant != self.tenant
        ]
        if any(conflicts):
            raise CrossTenantTryException(conflicts=conflicts)
        super(TenantAwareModel, self).save(*args, **kwargs)