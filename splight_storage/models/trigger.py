from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from splight_storage.models.tenant import TenantAwareModel
from splight_storage.models.asset import Asset, Attribute


class Trigger(TenantAwareModel):

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
        MONTHS = 'months', _('Months')


    asset = models.ForeignKey(Asset, related_name='asset_triggers', on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, related_name='attribute_triggers', on_delete=models.CASCADE)
    priority = models.CharField(max_length=8, choices=TriggerPriority.choices, default=TriggerPriority.HIGH)
    notification_message = models.TextField()
    condition = models.CharField(max_length=3, choices=Condition.choices, default=Condition.GREATER_EQUAL)
    value = models.FloatField()
    renotify = models.BooleanField()
    renotify_unit = models.CharField(max_length=7, choices=TimeUnit.choices, default=TimeUnit.MINUTES, null=True)
    renotify_time = models.IntegerField(null=True)