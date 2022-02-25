from unittest import TestCase


class TestShortcut(TestCase):
    def test_import_shortcut(self):
        from splight_lib.shortcut import asset_get, asset_set, get_asset_attributes