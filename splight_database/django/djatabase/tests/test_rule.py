from django.test import TestCase
from splight_database.django.djatabase.models.rule import Rule


class TestRule(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_create_rule(self):
        rule = Rule.objects.create(statement="A and B")
        self.assertIsInstance(rule, Rule)
        rule = Rule.objects.create(statement="A and B", variables = [{"key": "value"},{"key": 2}])
