from django.db import models
from .namespace import NamespaceAwareModel


class Dashboard(NamespaceAwareModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=10, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)


class Tab(NamespaceAwareModel):
    id = models.AutoField(primary_key=True)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name="solution_tabs")
    name = models.CharField(max_length=10, null=True, blank=True)


class Filter(NamespaceAwareModel):
    id = models.AutoField(primary_key=True)
    operator = models.CharField(max_length=10, null=True, blank=True)
    key = models.CharField(max_length=10, null=True, blank=True)
    value = models.CharField(max_length=10, null=True, blank=True)


class Chart(NamespaceAwareModel):
    id = models.AutoField(primary_key=True)
    tab = models.ForeignKey(Tab, on_delete=models.CASCADE, related_name="tab_charts")
    type = models.CharField(max_length=10, null=True, blank=True)
    filters = models.ManyToManyField(Filter)
    refresh_interval = models.CharField(max_length=10, null=True, blank=True)
    relative_window_time = models.CharField(max_length=10, null=True, blank=True)
