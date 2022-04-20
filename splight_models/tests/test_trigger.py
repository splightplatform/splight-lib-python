from parameterized import parameterized
from unittest import TestCase
from splight_models.trigger import Trigger, TriggerVariable


class TestTrigger(TestCase):

    @parameterized.expand([
        ("A and B == 2 or C == 's'",),
        ("A and not(A)",),
        ("A and A",),
        ("(A or A) and (A or A)",),
    ])
    def test_trigger_ok(self, rule):
        variables = [
            TriggerVariable(id='A', type=bool, filters={'asset_id__gte': 1}, key="args.value"),
            TriggerVariable(id='B', type=int, key="args.value"),
            TriggerVariable(id='C', type=str, key="args.value")
        ]
        Trigger(
            variables=variables,
            rule=rule
        )

    def test_trigger_nok(self):
        with self.assertRaises(ValueError):
            Trigger(
                variables=[
                    TriggerVariable(id='B', type=bool, key="args.value")
                ],
                rule="True and A"
            )