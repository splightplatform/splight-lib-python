from splight_models import *
from splight_lib import logging
from splight_lib.settings import setup


NotificationClient = setup.NOTIFICATION_CLIENT
DatalakeClient = setup.DATALAKE_CLIENT
DatabaseClient = setup.DATABASE_CLIENT
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
        variable = Variable(
            timestamp=notification.timestamp,
            args=notification.dict(),
        )
        datalake_client.save(instances=[variable], collection='notification')
    return
