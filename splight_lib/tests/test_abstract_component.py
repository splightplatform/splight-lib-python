from django.test import TestCase
from splight_lib.component.abstract import AbstractComponent
from splight_lib.asset import Asset
import os


class FakeComponent(AbstractComponent):
    managed_class = Asset

    def main_task(self):
        pass


class TestAbstractComponent(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_helthy_status(self):
        Asset.objects.create(name="test")
        component = FakeComponent(instance_id=1)
        self.assertTrue(os.path.isfile(component.health_file.name))
        component.mark_unhealthy()
        self.assertFalse(os.path.isfile(component.health_file.name))
