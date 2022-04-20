from unittest import TestCase


class TestTrigger(TestCase):
    def test_import_trigger(self):
        from splight_models.trigger import Trigger, TriggerVariable