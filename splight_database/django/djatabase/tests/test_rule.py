from django.test import TestCase
from splight_database.django.djatabase.models.rule import Rule, RuleVariable


class TestRule(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_create_rule(self):
        rule = Rule.objects.create(statement="A and B")
        self.assertIsInstance(rule, Rule)

    def test_create_rule_variable(self):
        var = RuleVariable.objects.create(
            collection="ACollection",
            key="key",
            type="str",
            filters={"key": "value"}
        )
        self.assertIsInstance(var, RuleVariable)
        rule = Rule.objects.create(statement="A and B")
        rule.variables.set([var])
        rule.save()
        self.assertIsInstance(rule, Rule)
