from unittest import TestCase


class TestComponent(TestCase):
    def test_import_component(self):
        from splight_lib.component import (
            AbstractAlgorithmComponent,
            AbstractNetworkComponent,
            AbstractClientComponent
        )