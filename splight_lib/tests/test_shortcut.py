from unittest import TestCase


class TestShortcut(TestCase):
    def test_import_shortcut(self):
        from splight_lib.shortcut import (
            asset_get,
            get_asset_attributes,
            notify,
            rule_eval,
        )