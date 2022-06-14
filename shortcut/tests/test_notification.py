from unittest.mock import patch
from django.test import TestCase
from splight_models import Notification
from splight_lib.database import DatabaseClient
from splight_lib.datalake import DatalakeClient
from splight_lib.notification import NotificationClient
from parameterized import parameterized
from shortcut import notify
from splight_database.django.djatabase.models.constants import ALGORITHM


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
            rule_id=1,
            source_id='3',
            source_type=ALGORITHM,
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
        self.assertEqual(len(self.datalake.get(Notification, id=notification.id, collection='notification')), 1)
        self.assertEqual(self.datalake.get(Notification, id=notification.id, collection='notification')[0], notification)
