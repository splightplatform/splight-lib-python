from parameterized import parameterized
from unittest import TestCase
from splight_models.rule import AlgorithmRule, RuleVariable, MappingRule
from splight_models.notification import (
    INFO, GREATER_THAN,
    GREATER_THAN_OR_EQUAL,
    LOWER_THAN,
    LOWER_THAN_OR_EQUAL,
    EQUAL
)


class TestAlgorithmRule(TestCase):

    @parameterized.expand([
        ("True and False",),
        ("True and 1",),
        ("True or 5 < 1",),
    ])
    def test_algorithm_rule_default(self, statement):
        AlgorithmRule(
            name="Rule1",
            description="",
            variables=[],
            statement=statement
        )

    @parameterized.expand([
        ("A and B == 2 or C == 's'",),
        ("A and not(A)",),
        ("A and A",),
        ("A and B",),
        ("(A or A) and (A or A)",),
        ("True and B > 1",),
    ])
    def test_algorithm_rule_ok(self, statement):
        variables = [
            RuleVariable(id='A', type="bool", filters={'asset_id__gte': 1}, key="args.value"),
            RuleVariable(id='B', type="float", key="args.value"),
            RuleVariable(id='C', type="str", key="args.value")
        ]
        AlgorithmRule(
            name="Rule1",
            description="",
            variables=variables,
            statement=statement
        )

    @parameterized.expand([
        ("True and A",),
        ("True and B > '1'",),
    ])
    def test_algorithm_rule_nok(self, statement):
        with self.assertRaises(ValueError):
            variables = [
                RuleVariable(id='B', type="float", key="args.value")
            ]
            AlgorithmRule(
                name="Rule1",
                description="",
                variables=variables,
                statement=statement
            )


class TestMappingRule(TestCase):
    def test_mapping_rule_ok(self):
        MappingRule(
            asset_id="123",
            attribute_id="123",
            value="4",
            type="float",
            message="This is a sample message for the event description",
            severity=INFO,
            operator=GREATER_THAN,
        )

    @parameterized.expand([
        ('str', GREATER_THAN, 5, False),
        ('str', GREATER_THAN, 4, True),
        ('str', GREATER_THAN_OR_EQUAL, 5, True),
        ('str', GREATER_THAN_OR_EQUAL, 6, False),
        ('str', LOWER_THAN, 6, True),
        ('str', LOWER_THAN, 2, False),
        ('str', LOWER_THAN_OR_EQUAL, 2, False),
        ('float', LOWER_THAN_OR_EQUAL, 5, True),
        ('float', LOWER_THAN_OR_EQUAL, 6, True),
        ('float', EQUAL, 5, True),
        ('float', EQUAL, 2, False),
    ])
    def test_mapping_rule_eval(self, type, operator, value, expected_result):
        rule = MappingRule(
            asset_id="123",
            attribute_id="123",
            value="5",
            type=type,
            message="This is a sample message for the event description",
            severity=INFO,
            operator=operator,
        )
        self.assertTrue(rule.is_satisfied(value) is expected_result)
