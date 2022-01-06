from django.db import models


class CrossTenantTryException(Exception):
    def __init__(self, tenant, conflicts, *args, **kwargs) -> None:
        self.conflicts = conflicts
        self.tenant = tenant
        message = f"Found conflicts in fields: {conflicts}. Current tenant: {self.tenant}"
        super().__init__(message, *args, **kwargs)


class Tenant(models.Model):
    org_id = models.CharField(max_length=100)
    # subdomain_prefix = models.CharField(max_length=100, unique=True)

    def __repr__(self):
        return f"<Tenant {self.org_id}>"

    def __str__(self):
        return self.org_id


class TenantAwareModel(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, default=None, null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ['-id']

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
            field.name for field in tenant_foreign_keys
            if getattr(self, field.name).tenant != self.tenant
        ]
        if any(conflicts):
            raise CrossTenantTryException(tenant=self.tenant, conflicts=conflicts)
        super(TenantAwareModel, self).save(*args, **kwargs)