from unittest import TestCase


class TestShortcut(TestCase):
    def test_import_shortcut(self):
        from splight_lib.shortcut import (
            notify,
            save_file,
            OrganizationHandler,
        )