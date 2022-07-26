from django.test import TestCase
from splight_database.django.djatabase.models import Asset


class TestAlgorithm(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_logical_delete(self):
        asset = Asset.objects.create(name="Asset", description="Description")
        self.assertEqual(asset.deleted, False)
        asset.delete()
        self.assertEqual(asset.deleted, True)
