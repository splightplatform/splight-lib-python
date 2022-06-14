from splight_lib.database import DatabaseClient
from splight_lib.datalake import DatalakeClient
from splight_lib.notification import NotificationClient
from splight_models import *
from splight_lib import logging


logger = logging.getLogger()


def notify(notification: Notification,
           database_client: DatabaseClient = None,
           notification_client: NotificationClient = None,
           datalake_client: DatalakeClient = None) -> None:
    logger.debug(f"Notification sent: {notification}")
    if database_client:
        notification = database_client.save(notification)
    if notification_client:
        notification_client.send(notification)
    if datalake_client:
        datalake_client.save(Notification, instances=[notification], collection='notification')
    return
