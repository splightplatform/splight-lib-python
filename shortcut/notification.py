from splight_lib.communication import Variable
from splight_lib.database import DatabaseClient
from splight_lib.notification import NotificationClient
from splight_models import *
from splight_lib import logging


logger = logging.getLogger()


def notify(notification: Notification, database_client: DatabaseClient, notification_client: NotificationClient) -> None:
    logger.debug(f"Notification sent: {notification}")
    notification = database_client.save(notification)
    notification_client.send(notification)
    return
