from django.db import models
from splight_storage.models.tag import Tag
from splight_storage.models.tenant import TenantAwareModel


class DigitalOfferComponent(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class DigitalOffer(models.Model):
    name = models.CharField(max_length=100)
    components = models.ManyToManyField(
        DigitalOfferComponent, related_name='digital_offers')

    def __str__(self):
        return self.name


class RunningDigitalOffer(TenantAwareModel):
    tag = models.ForeignKey(Tag, related_name="digital_offers", on_delete=models.CASCADE, null=True)
    digital_offer = models.ForeignKey(DigitalOffer, related_name='running', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.digital_offer}@{self.tag}-{self.tenant.org_id}"