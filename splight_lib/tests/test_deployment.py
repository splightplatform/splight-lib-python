from unittest import TestCase


class TestDeployment(TestCase):
    def test_import_deployment(self):
        from splight_abstract.deployment import AbstractDeploymentClient