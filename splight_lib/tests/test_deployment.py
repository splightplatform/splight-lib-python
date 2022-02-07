from unittest import TestCase


class TestCommunication(TestCase):
    def test_import_deployment(self):
        from splight_lib.deployment import DeploymentClient