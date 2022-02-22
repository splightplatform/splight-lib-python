from django.test import TestCase
from splight_database.django.djatabase.models.asset import Asset, Attribute
from splight_database.django.djatabase.models.mapping import ValueMapping
from splight_database.django.djatabase.models.trigger import Trigger, TriggerGroup, TriggerGroupLimitException
import os


class TestTrigger(TestCase):
    def setUp(self) -> None:
        self.asset = Asset.objects.create(name="Asset1")
        self.attribute = Attribute.objects.create(name="p")
        self.value_mapping = ValueMapping.objects.create(asset=self.asset, attribute=self.attribute, value=1)
        return super().setUp()

    def test_create_trigger_group(self):
        trigger_group = TriggerGroup.objects.create(name="Group1")
        self.assertIsInstance(trigger_group, TriggerGroup)

    def test_create_trigger(self):
        trigger_group = TriggerGroup.objects.create(name="Group1")
        trigger = Trigger.objects.create(
            trigger_group=trigger_group,
            asset=self.asset,
            attribute=self.attribute,
            condition='gte',
            priority='high',
            value=1,
            notification_message="message",
            renotify=True,
            renotify_unit="minutes",
            renotify_time=1
        )
        self.assertIsInstance(trigger, Trigger)

    def test_group_limit(self):
        trigger_group = TriggerGroup.objects.create(name="Group1")
        for _ in range(os.getenv("MAX_TRIGGERS_PER_GROUP", 20)):
            trigger = Trigger.objects.create(
                trigger_group=trigger_group,
                asset=self.asset,
                attribute=self.attribute,
                condition='gte',
                priority='high',
                value=1,
                notification_message="message",
                renotify=True,
                renotify_unit="minutes",
                renotify_time=1
            )
            self.assertIsInstance(trigger, Trigger)
        with self.assertRaises(TriggerGroupLimitException):
            Trigger.objects.create(
                trigger_group=trigger_group,
                asset=self.asset,
                attribute=self.attribute,
                condition='gte',
                priority='high',
                value=1,
                notification_message="message",
                renotify=True,
                renotify_unit="minutes",
                renotify_time=1
            )
