from django.db import models
from django.utils.translation import gettext_lazy as _
from splight_storage.models.tenant import TenantAwareModel
from splight_storage.models.asset import Asset, Attribute
from typing import Callable
import os


class TriggerGroupLimitException(Exception):
    def __init__(self, *args, **kwargs) -> None:
        message: str = "You have exceeded the maximum number of triggers per group."
        super().__init__(message, *args, **kwargs)


class TriggerGroup(TenantAwareModel):
    name = models.CharField(max_length=80)


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

        super(Trigger, self).save(*args, **kwargs)


    @property
    def condition_is_valid(self) -> Callable[[float], bool]:
        EPS = 5e-2

        if self.condition == 'gt':
            return lambda a : a > self.value if a is not None else False 
        if self.condition == 'lt':
            return lambda a : a < self.value if a is not None else False 
        if self.condition == 'lte':
            return lambda a : a <= self.value if a is not None else False 
        if self.condition == 'gte':
            return lambda a : a >= self.value if a is not None else False 
        if self.condition == 'eq':
            return lambda a : abs(a - self.value) < EPS if a is not None else False 
        if self.condition == 'ne':
            return lambda a : abs(a - self.value) > EPS if a is not None else False