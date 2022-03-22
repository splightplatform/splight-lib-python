import json
from unittest import TestCase
from pydantic import ValidationError
from splight_models import Variable, Message, Action


class TestVariable(TestCase):
    def test_variable_json(self):
        variable_data = {
            "args": {},
            "path": "path1",
            "asset_id": "id1",
            "attribute_id": "1",
        }
        variable = Variable(**variable_data)
        self.assertIsInstance(variable.json(), str)
        variable_data["timestamp"] = None
        self.assertEqual(variable.json(), json.dumps(variable_data))

    def test_variable_dict(self):
        variable_data = {
            "args": {},
            "path": "path1",
            "attribute_id": "1",
            "asset_id": "id1"
        }
        variable = Variable(**variable_data)
        self.assertIsInstance(variable.dict(), dict)
        variable_data["timestamp"] = None
        self.assertDictEqual(variable.dict(), variable_data)

    def test_variable_defaults(self):
        variable_data = {
            "args": {}
        }
        variable = Variable(**variable_data)
        self.assertTrue(hasattr(variable, "path"))
        self.assertTrue(hasattr(variable, "args"))
        self.assertTrue(hasattr(variable, "attribute_id"))
        self.assertTrue(hasattr(variable, "asset_id"))


class TestMessage(TestCase):
    def test_message_json(self):
        message_data = {
            "action": Action.WRITE,
            "variables": []
        }
        message = Message(**message_data)
        self.assertIsInstance(message.json(), str)
        self.assertEqual(message.json(), json.dumps(message_data))

    def test_message_dict(self):
        message_data = {
            "action": Action.WRITE,
            "variables": []
        }
        message = Message(**message_data)
        self.assertIsInstance(message.dict(), dict)
        self.assertDictEqual(message.dict(), message_data)

    def test_message_variables_typed(self):
        message_data = {
            "action": Action.WRITE,
            "variables": [
                Variable(attribute_id="1", args={}),
                Variable(attribute_id="2", args={}),
                Variable(attribute_id="3", args={})
            ]
        }
        message = Message(**message_data)
        self.assertIsInstance(message.dict(), dict)
        self.assertDictEqual(message.dict(), message_data)
        message_data = {
            "action": Action.WRITE,
            "variables": [1, 2, 3]
        }
        with self.assertRaises(ValidationError):
            message = Message(**message_data)
