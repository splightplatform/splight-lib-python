from django.db import models


class CrossTenantTryException(Exception):
    pass


class Tenant(models.Model):
    org_id = models.CharField(max_length=100)
    # subdomain_prefix = models.CharField(max_length=100, unique=True)


class TenantAwareModel(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, default=None, null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Check consistency between TenantAwareModels
        nested_model_names = [field for field in self._meta.local_fields]
        nested_tenant_aware_models = [
            field for field in nested_model_names
            if isinstance(getattr(self, field.name), TenantAwareModel)
        ]
        conflicts = [
            field for field in nested_tenant_aware_models
            if getattr(self, field.name).tenant != self.tenant
        ]
        if any(conflicts):
            raise CrossTenantTryException
        super(TenantAwareModel, self).save(*args, **kwargs)