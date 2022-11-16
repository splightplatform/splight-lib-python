from unittest import TestCase
from parameterized import parameterized
from splight_lib.shortcut import notify
from fake_splight_lib.database import FakeDatabaseClient as DatabaseClient
from fake_splight_lib.datalake import FakeDatalakeClient as DatalakeClient
from fake_splight_lib.notification import FakeNotificationClient as NotificationClient
from splight_models.notification import SourceType
from splight_models import Notification, Variable


class TestNotification(TestCase):
    def setUp(self):
        self.namespace = "default"
        self.database = DatabaseClient(self.namespace)
        self.datalake = DatalakeClient(self.namespace)
        self.notifier = NotificationClient(self.namespace)
        return super().setUp()

    @parameterized.expand([
        (Notification(
            message="Message sample",
            title="Title sample"
        ),),
        (Notification(
            message="Message sample",
            title="Title sample",
            asset_id=1,
            attribute_id=1,
        ),),
        (Notification(
            message="Message sample",
            title="Title sample",
            asset_id=1,
            attribute_id=1,
            source_id='3',
            source_type=SourceType.algorithm,
        ),),
    ])
    def test_notify(self, notification):
        notify(
            notification=notification,
            database_client=self.database,
            datalake_client=self.datalake,
            notification_client=self.notifier)
        self.assertEqual(len(self.database.get(Notification, id=notification.id)), 1)
        self.assertEqual(self.database.get(Notification, id=notification.id)[0], notification)
        self.assertEqual(len(self.datalake.get(Variable, args__id=notification.id, collection='notification')), 1)
        self.assertEqual(self.datalake.get(Variable, args__id=notification.id, collection='notification')[0].args, notification.dict())
        self.assertEqual(self.datalake.get(Variable, args__id=notification.id, collection='notification')[0].timestamp, notification.dict().get('timestamp'))
