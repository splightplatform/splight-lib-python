import uuid
from django.db import models


class CrossNamespaceTryException(Exception):
    def __init__(self, namespace, conflicts, *args, **kwargs) -> None:
        self.namespace = namespace
        self.conflicts = conflicts
        message = f"Found conflicts in fields: {conflicts}. Current tenant: {self.namespace}"
        super().__init__(message, *args, **kwargs)


class Namespace(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default="default")
    environment = models.JSONField(default=dict)

    def to_dict(self):
        return self.__dict__


class NamespaceAwareModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    namespace = models.ForeignKey(Namespace, on_delete=models.CASCADE, default=None, null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ['-id']

    def save(self, *args, **kwargs):
        # Check consistency between NamespacesAwareModels
        nested_foreign_key = [
            field for field in self._meta.local_fields
            if type(field) == models.ForeignKey
        ]
        namespace_foreign_keys = [
            field for field in nested_foreign_key
            if isinstance(getattr(self, field.name), NamespaceAwareModel)
        ]
        conflicts = [
            field.name for field in namespace_foreign_keys
            if getattr(self, field.name).namespace != self.namespace
        ]
        if any(conflicts):
            raise CrossNamespaceTryException(namespace=self.namespace, conflicts=conflicts)
        super(NamespaceAwareModel, self).save(*args, **kwargs)

    def to_dict(self):
        data = self.__dict__
        for key, value in data.items():
            if isinstance(value, uuid.UUID):
                data[key] = str(value)
        for m2m_field in self._meta.local_many_to_many:
            data[m2m_field.name] = [t.id for t in getattr(self, m2m_field.name).all()]
        return data
