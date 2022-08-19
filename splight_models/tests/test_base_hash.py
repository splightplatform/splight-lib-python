from unittest import TestCase
from splight_models.base import SplightBaseModel
from datetime import datetime
from splight_models import *

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
    args = {'name': ""}
    rand_str_arg = 'name'

class TestAttributeHash(AbstractBaseHash, TestCase):
    class_model = Attribute
    args = {'name': ""}
    rand_str_arg = 'name'

class TestDashboardHash(AbstractBaseHash, TestCase):
    class_model = Dashboard
    args = {'name': ""}
    rand_str_arg = 'name'

class TestTabHash(AbstractBaseHash, TestCase):
    class_model = Tab
    args = {'name': "", 'dashboard_id': 'id'}
    rand_str_arg = 'name'

class TestFilterHash(AbstractBaseHash, TestCase):
    class_model = Filter
    args = {'chart_item_id': 'id', 'key' : 'key', 'value': 'value', 'label': 'label'}
    rand_str_arg = 'key'

class TestChartItemHash(AbstractBaseHash, TestCase):
    class_model = ChartItem
    args = {'chart_id': 'id'}
    rand_str_arg = 'chart_id'

class TestChartHash(AbstractBaseHash, TestCase):
    class_model = Chart
    args = {
        'tab_id': 'id',
        'type': 'type',     
        'position_x': 0,
        'position_y': 0,
        'height': 0,
        'width': 0,
        'min_height': 0,
        'min_width': 0
    }
    rand_str_arg = 'tab_id'

class TestDeploymentHash(AbstractBaseHash, TestCase):
    class_model = Deployment
    args = {'version': 'ver', 'type': 'type'}
    rand_str_arg = 'version'

class TestGeopointHash(AbstractBaseHash, TestCase):
    class_model = Geopoint
    args = {'id': 'id', 'latitude': 0.1, 'longitude': 0.2}
    rand_str_arg = 'id'

class TestMappingHash(AbstractBaseHash, TestCase):
    class_model = Mapping
    args = {'id': 'id'}
    rand_str_arg = 'id'

class TestValueMappingHash(AbstractBaseHash, TestCase):
    class_model = ValueMapping
    args = {'asset_id': '1', 'attribute_id': '1', 'value': 'val'}
    rand_str_arg = 'asset_id'

class TestReferenceMappingHash(AbstractBaseHash, TestCase):
    class_model = ReferenceMapping
    args = {'asset_id': '1', 'attribute_id': '1', 'ref_asset_id': 'val', 'ref_attribute_id': 'val'}
    rand_str_arg = 'asset_id'

class TestClientMappingHash(AbstractBaseHash, TestCase):
    class_model = ClientMapping
    args = {'asset_id': '1', 'attribute_id': '1', 'connector_id': 'val', 'path': 'val'}
    rand_str_arg = 'asset_id'

class TestServerMappingHash(AbstractBaseHash, TestCase):
    class_model = ServerMapping
    args = {'asset_id': '1', 'attribute_id': '1', 'connector_id': 'val', 'path': 'val'}
    rand_str_arg = 'asset_id'

class TestMessageHash(AbstractBaseHash, TestCase):
    class_model = Message
    args = {'action': '1', 'variables': []}
    rand_str_arg = 'action'

class TestNamespaceHash(AbstractBaseHash, TestCase):
    class_model = Namespace
    args = {'id': '1'}
    rand_str_arg = 'id'

class TestNetTargetHash(AbstractBaseHash, TestCase):
    class_model = NetTarget
    args = {'ip': '1', 'port': '1'}
    rand_str_arg = 'ip'

class TestNotificationHash(AbstractBaseHash, TestCase):
    class_model = Notification
    args = {'title': '1', 'message': '1', 'timestamp': datetime.now()}
    rand_str_arg = 'title'

class TestRuleHash(AbstractBaseHash, TestCase):
    class_model = AlgorithmRule
    args = {'name': '1', 'statement': '1'}
    rand_str_arg = 'name'

class TestRuleVariableHash(AbstractBaseHash, TestCase):
    class_model = RuleVariable
    args = {'id': '1'}
    rand_str_arg = 'id'

class TestMappingRule(AbstractBaseHash, TestCase):
    class_model = MappingRule
    args = {'id': '1', 'message': 'message', 'value': 'value', 'asset_id': '2', 'attribute_id': '2'}
    rand_str_arg = 'message'

class TestRunnerHash(AbstractBaseHash, TestCase):
    class_model = Runner
    args = {'name': '1', 'version': '1'}
    rand_str_arg = 'name'

class TestAlgorithmHash(AbstractBaseHash, TestCase):
    class_model = Algorithm
    args = {'name': '1', 'version': '1'}
    rand_str_arg = 'name'

class TestNetworkHash(AbstractBaseHash, TestCase):
    class_model = Network
    args = {'name': '1', 'version': '1'}
    rand_str_arg = 'name'

class TestConnectorHash(AbstractBaseHash, TestCase):
    class_model = Connector
    args = {'name': '1', 'version': '1'}
    rand_str_arg = 'name'

class TestStorageFileHash(AbstractBaseHash, TestCase):
    class_model = StorageFile
    args = {'file': '1'}
    rand_str_arg = 'file'

class TestTagHash(AbstractBaseHash, TestCase):
    class_model = Tag
    args = {'name': '1'}
    rand_str_arg = 'name'

class TestVariableHash(AbstractBaseHash, TestCase):
    class_model = Variable
    args = {'path': '1', 'args': {}, 'timestamp': datetime.now()}
    rand_str_arg = 'path'