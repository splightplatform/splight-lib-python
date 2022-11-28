from datetime import datetime
from unittest import TestCase

from splight_models import *
from splight_models.base import SplightBaseModel


class AbstractBaseHash(object):
    class_model = SplightBaseModel
    args = {}
    rand_str_arg = ""

    def test_eq_hash(self):
        obj1 = self.class_model(**self.args)
        obj2 = self.class_model(**self.args)
        self.assertEqual(obj1.__hash__(), obj2.__hash__())

    def test_neq_hash(self):
        obj1_args = self.args.copy()
        obj2_args = self.args.copy()
        obj1_args[self.rand_str_arg] = "randstr1"
        obj2_args[self.rand_str_arg] = "randstr2"
        obj1 = self.class_model(**obj1_args)
        obj2 = self.class_model(**obj2_args)
        self.assertNotEqual(obj1.__hash__(), obj2.__hash__())


class TestAssetHash(AbstractBaseHash, TestCase):
    class_model = Asset
    args = {"name": ""}
    rand_str_arg = "name"


class TestAttributeHash(AbstractBaseHash, TestCase):
    class_model = Attribute
    args = {"name": ""}
    rand_str_arg = "name"


class TestDeploymentHash(AbstractBaseHash, TestCase):
    class_model = Deployment
    args = {"version": "ver", "type": "Component"}
    rand_str_arg = "version"


class TestGeopointHash(AbstractBaseHash, TestCase):
    class_model = Geopoint
    args = {"id": "id", "latitude": 0.1, "longitude": 0.2}
    rand_str_arg = "id"


class TestMappingHash(AbstractBaseHash, TestCase):
    class_model = Mapping
    args = {
        "name": "MyMapping",
        "asset_id": "1",
        "attribute_id": "1",
        "output_format": "Number",
    }
    rand_str_arg = "asset_id"


class TestMessageHash(AbstractBaseHash, TestCase):
    class_model = Message
    args = {"action": "1", "variables": []}
    rand_str_arg = "action"


class TestNamespaceHash(AbstractBaseHash, TestCase):
    class_model = Namespace
    args = {"id": "1"}
    rand_str_arg = "id"


class TestNetTargetHash(AbstractBaseHash, TestCase):
    class_model = NetTarget
    args = {"ip": "1", "port": "1"}
    rand_str_arg = "ip"


class TestNotificationHash(AbstractBaseHash, TestCase):
    class_model = Notification
    args = {"title": "1", "message": "1", "timestamp": datetime.now()}
    rand_str_arg = "title"

class TestComponentHash(AbstractBaseHash, TestCase):
    class_model = Component
    args = {"name": "1", "version": "1"}
    rand_str_arg = "name"

class TestStorageFileHash(AbstractBaseHash, TestCase):
    class_model = StorageFile
    args = {"file": "1"}
    rand_str_arg = "file"


class TestTagHash(AbstractBaseHash, TestCase):
    class_model = Tag
    args = {"name": "1"}
    rand_str_arg = "name"


class TestVariableHash(AbstractBaseHash, TestCase):
    class_model = Variable
    args = {"path": "1", "args": {}, "timestamp": datetime.now()}
    rand_str_arg = "path"
