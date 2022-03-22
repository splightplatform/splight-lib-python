from django.db import models


class Algorithm(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)
    version = models.CharField(max_length=100)
    parameters = models.JSONField()

    def to_dict(self):
        data = self.__dict__
        return data