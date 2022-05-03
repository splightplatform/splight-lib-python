from django.test import TestCase
from splight_models import Notification
from splight_lib.database import DatabaseClient
from splight_lib.notification import NotificationClient
from shortcut import notify


class TestNotification(TestCase):
    def setUp(self):
        self.namespace = "default"
        self.database = DatabaseClient(self.namespace)
        self.datalake = NotificationClient(self.namespace)
        self.notification = Notification(message="Message sample", title="Title sample")
        return super().setUp()

    def test_notify(self):
        self.assertEqual(len(self.database.get(Notification)), 0)
        notify(notification=self.notification, database_client=self.database, notification_client=self.datalake)
        self.assertEqual(len(self.database.get(Notification)), 1)
        self.assertEqual(self.database.get(Notification)[0], self.notification)
