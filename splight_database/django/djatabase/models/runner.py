from unicodedata import category
from django.db import models
from django.utils.translation import gettext_lazy as _
from .namespace import NamespaceAwareModel


class Category(models.TextChoices):
    ALGORITHM = 'algorithm', _('Algorithm')
    CONNECTOR = 'connector', _('Connector')
    NETWORK = 'network', _('Network')
    TRIGGER_HANDLER = 'trigger-handler', _('Trigger handler')


class Runner(NamespaceAwareModel):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)
    # TODO remove tag_id
    tag_id = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=50, choices=Category.choices, default=Category.ALGORITHM)
    version = models.CharField(max_length=100, null=True, blank=True)
    parameters = models.JSONField()