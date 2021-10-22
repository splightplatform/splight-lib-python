from django.db import models
from model_utils.managers import InheritanceManager

class ConnectorInterface(models.Model):
    objects = InheritanceManager()

    class Meta:
        app_label = 'splight_storage'
