import os
from splight_notification import *
from fake_splight_lib.notification import FakeNotificationClient

SELECTOR = {
    'fake': FakeNotificationClient,
    'pusher': PusherClient
}

NotificationClient = SELECTOR.get(os.environ.get('NOTIFICATION', 'fake'))
