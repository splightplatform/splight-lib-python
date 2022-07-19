import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class BlockchainContract(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)
    account_id = models.CharField(max_length=100, null=True, blank=True)
    abi_json = models.JSONField(default=dict)

    def to_dict(self):
        data = self.__dict__
        for key, value in data.items():
            if isinstance(value, uuid.UUID):
                data[key] = str(value)
        return data