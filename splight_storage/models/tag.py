from django.db import models


class Tag(models.Model):
    type = models.CharField(max_length=100)
    value = models.CharField(max_length=100, blank=True)
