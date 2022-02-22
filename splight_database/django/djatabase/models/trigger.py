from django.db import models
from django.utils.translation import gettext_lazy as _
from .namespace import NamespaceAwareModel
from .asset import Asset, Attribute
from .mapping import ValueMapping, ClientMapping, ReferenceMapping, Mapping
from splight_models.exception import TriggerGroupLimitException
import os


class TriggerGroup(NamespaceAwareModel):
    name = models.CharField(max_length=80)


class Trigger(NamespaceAwareModel):

    class TriggerPriority(models.TextChoices):
        HIGH = 'high', _('High priority')
        STANDARD = 'standard', _('Standard priority')

    class Condition(models.TextChoices):
        GREATER = 'gt', _('Greater')
        LOWER = 'lt', _('Lower')
        LOWER_EQUAL = 'lte', _('Lower or equal')
        GREATER_EQUAL = 'gte', _('Greater or equal')
        EQUAL = 'eq', _('Equal')
        NOT_EQUAL = 'ne', _('Not equal')


    class TimeUnit(models.TextChoices):
        MINUTES = 'minutes', _('Minutes')
        HOURS = 'hours', _('Hours')
        DAYS = 'days', _('Days')
        WEEKS = 'weeks', _('Weeks')

    trigger_group = models.ForeignKey(TriggerGroup, related_name='triggers', on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, related_name='asset_triggers', on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, related_name='attribute_triggers', on_delete=models.CASCADE)
    priority = models.CharField(max_length=8, choices=TriggerPriority.choices, default=TriggerPriority.HIGH)
    notification_message = models.TextField()
    condition = models.CharField(max_length=3, choices=Condition.choices, default=Condition.GREATER_EQUAL)
    value = models.FloatField()
    renotify = models.BooleanField()
    renotify_unit = models.CharField(max_length=7, choices=TimeUnit.choices, default=TimeUnit.MINUTES, null=True)
    renotify_time = models.IntegerField(null=True)


    def save(self, *args, **kwargs):
        group_limit = os.getenv("MAX_TRIGGERS_PER_GROUP", 20)

        if Trigger.objects.filter(trigger_group = self.trigger_group).count() >= group_limit:
            raise TriggerGroupLimitException()

        mappings = [ValueMapping.objects.filter(asset=self.asset, attribute=self.attribute).exists(),
                    ClientMapping.objects.filter(asset=self.asset, attribute=self.attribute).exists(),
                    ReferenceMapping.objects.filter(asset=self.asset, attribute=self.attribute).exists()]

        if not any(mappings):
            raise Mapping.DoesNotExist(f"Asset id: {self.asset.id} has no mapping for attribute id {self.attribute.id}.")

        super(Trigger, self).save(*args, **kwargs)
