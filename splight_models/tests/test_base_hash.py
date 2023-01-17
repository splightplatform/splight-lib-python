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
    args = {"version": "ver"}
    rand_str_arg = "version"


class TestNamespaceHash(AbstractBaseHash, TestCase):
    class_model = Namespace
    args = {"id": "1"}
    rand_str_arg = "id"


class TestNotificationHash(AbstractBaseHash, TestCase):
    class_model = Notification
    args = {"title": "1", "message": "1", "timestamp": datetime.now()}
    rand_str_arg = "title"


class TestComponentHash(AbstractBaseHash, TestCase):
    class_model = Component
    args = {"name": "1", "version": "1"}
    rand_str_arg = "name"
