from django.db import models
from .tag import Tag
from .namespace import NamespaceAwareModel


class DigitalOfferComponent(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def to_dict(self):
        return self.__dict__


class DigitalOffer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    components = models.ManyToManyField(
        DigitalOfferComponent, related_name='digital_offers')

    def __str__(self):
        return self.name

    def to_dict(self):
        data = self.__dict__
        for m2m_field in self._meta.local_many_to_many:
            data[m2m_field.name] = [t.id for t in getattr(self, m2m_field.name).all()]
        return data

class RunningDigitalOffer(NamespaceAwareModel):
    tag = models.ForeignKey(Tag, related_name="digital_offers", on_delete=models.CASCADE, null=True)
    digital_offer = models.ForeignKey(DigitalOffer, related_name='running', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.digital_offer}@{self.tag}-{self.tenant.org_id}"
    
    def to_dict(self):
        return self.__dict__