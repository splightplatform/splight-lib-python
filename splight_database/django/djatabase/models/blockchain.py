from django.utils.translation import gettext_lazy as _
from django.db.utils import IntegrityError
from django.db import models
from .namespace import NamespaceAwareModel
from .delete import LogicalDeleteModel
import uuid


class BlockchainContract(LogicalDeleteModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    abi_json = models.JSONField(default=dict)

    def to_dict(self):
        data = self.__dict__
        for key, value in data.items():
            if isinstance(value, uuid.UUID):
                data[key] = str(value)
        return data


class BlockchainContractSubscription(NamespaceAwareModel):
    asset_id = models.CharField(null=True, max_length=100)
    attribute_id = models.CharField(null=True, max_length=100)
    contract_id = models.CharField(null=True, max_length=100)
    last_checkpoint = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if BlockchainContractSubscription.objects.filter(asset_id=self.asset_id,
                                                         attribute_id=self.attribute_id,
                                                         contract_id=self.contract_id,
                                                         deleted=False).exclude(id=self.id):
            raise IntegrityError

        return super().save(*args, **kwargs)
