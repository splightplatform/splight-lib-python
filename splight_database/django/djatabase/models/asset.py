from django.db import models
from .namespace import NamespaceAwareModel
from .tag import Tag
from .geopoint import Geopoint


class DuplicatedAttribute(Exception):
    pass


class Asset(NamespaceAwareModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100)
    tags = models.ManyToManyField(Tag, blank=True)
    geopoints = models.ManyToManyField(Geopoint, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)

    def to_dict(self):
        data = self.__dict__
        data["tags"] = [t.id for t in self.tags.all()]
        return data


class Attribute(NamespaceAwareModel):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if Attribute.objects.filter(name=self.name, namespace=self.namespace):
            raise DuplicatedAttribute
        super(Attribute, self).save(*args, **kwargs)
