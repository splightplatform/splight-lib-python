from django.test import TestCase
from splight_database.django.djatabase.models.algorithm import Algorithm


class TestAlgorithm(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_create_network(self):
        conn = Algorithm.objects.create(name="Algorithm", description="Description", version="A_VERSION", parameters=[{"key": "value"}])
        self.assertIsInstance(conn, Algorithm)
