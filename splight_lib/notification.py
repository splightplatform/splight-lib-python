import os
import ast
from splight_notification import *
from fake_splight_lib.notification import FakeNotificationClient

NotificationClient = PusherClient

if ast.literal_eval(os.getenv("FAKE_NOTIFICATION", "True")):
    NotificationClient = FakeNotificationClient
