import uuid
from django.test import TestCase
from splight_models import RuleVariable, Rule
from splight_lib.database import DatabaseClient
from splight_lib.datalake import DatalakeClient
from shortcut import rule_eval
from splight_models.variable import Variable


class TestRuleEval(TestCase):
    def setUp(self):
        self.namespace = "default"
        self.database = DatabaseClient(self.namespace)
        self.datalake = DatalakeClient(self.namespace)
        self.filters_A = {"asset_id": str(uuid.uuid4()), "attribute_id": "123"}
        self.filters_B = {"asset_id": str(uuid.uuid4()), "attribute_id": "234"}
        variables = [
                RuleVariable(id='A', type="bool", filters=self.filters_A, key="args__value"),
                RuleVariable(id='B', type="int", filters=self.filters_B, key="args__value"),
                RuleVariable(id='C', type="str", key="args__value")
            ]
        self.rule = Rule(
                name="Rule1",
                description="",
                variables=variables,
                statement="A and B > 5"
            )
        self.database.save(self.rule)
        return super().setUp()

    def test_rule_evaluation_false(self):
        self.assertFalse(rule_eval(rule_id=self.rule.id, db_client=self.database, dl_client=self.datalake))

    def test_rule_evaluation_true(self):
        data = [
            Variable(args={"value": True}, **self.filters_A),
            Variable(args={"value": 7}, **self.filters_B),
        ]
        self.datalake.save(Variable, instances=data)
        self.assertTrue(rule_eval(rule_id=self.rule.id, db_client=self.database, dl_client=self.datalake))

    def test_unexistent_rule_evaluation(self):
        self.assertIsNone(rule_eval(rule_id='123', db_client=self.database, dl_client=self.datalake))