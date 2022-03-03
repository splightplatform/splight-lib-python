from django.db import models
from .trigger import Trigger


class Notification(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default="default")
    trigger_id = models.ForeignKey(Trigger, on_delete=models.CASCADE)
    priority = models.CharField(max_length=8)
    message = models.TextField()
    value = models.FloatField()
    update_timestamp = models.DateTimeField(auto_now=True)

    def to_dict(self):
        return self.__dict__