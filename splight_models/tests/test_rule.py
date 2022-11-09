from parameterized import parameterized
from unittest import TestCase
from splight_models.rule import Rule
from splight_models.datalake import DatalakeOutputQuery
from splight_models.notification import (
    INFO, GREATER_THAN,
    GREATER_THAN_OR_EQUAL,
    LOWER_THAN,
    LOWER_THAN_OR_EQUAL,
    EQUAL
)

class TestRule(TestCase):
    def test_rule_ok(self):
        Rule(
            query=DatalakeOutputQuery(
                source="Algorithm",
                component_id="01d08df6-e9f6-489c-ad62-9c8e6b714412",
                output_format="Value",
                target="value",
                filters={},
                timezone_offset=0.0
            ),
            value="4",
            type="float",
            message="This is a sample message for the event description",
            severity=INFO,
            operator=GREATER_THAN,
        )

    @parameterized.expand([
        ('str', GREATER_THAN, 5, False),
        ('str', GREATER_THAN, 4, False),
        ('str', GREATER_THAN_OR_EQUAL, 5, True),
        ('str', GREATER_THAN_OR_EQUAL, 6, True),
        ('str', LOWER_THAN, 6, False),
        ('str', LOWER_THAN, 2, True),
        ('str', LOWER_THAN_OR_EQUAL, 2, True),
        ('float', LOWER_THAN_OR_EQUAL, 5, True),
        ('float', LOWER_THAN_OR_EQUAL, 6, False),
        ('float', EQUAL, 5, True),
        ('float', EQUAL, 2, False),
    ])
    def test_rule_eval(self, type, operator, value, expected_result):
        rule = Rule(
            query=DatalakeOutputQuery(
                source="Algorithm",
                component_id="01d08df6-e9f6-489c-ad62-9c8e6b714412",
                output_format="Value",
                target="value",
                filters={},
                timezone_offset=0.0
            ),
            value="5",
            type=type,
            message="This is a sample message for the event description",
            severity=INFO,
            operator=operator,
        )
        self.assertTrue(rule.is_satisfied(value) is expected_result)
