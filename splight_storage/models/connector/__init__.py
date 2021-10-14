from django.db import models


class ConnectorInterface(models.Model):
    class Meta:
        app_label = 'splight_storage'
