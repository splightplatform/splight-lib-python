from django.db import models
from .namespace import NamespaceAwareModel


class Dashboard(NamespaceAwareModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)


class Tab(NamespaceAwareModel):
    id = models.AutoField(primary_key=True)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name="dashboard_tabs")
    name = models.CharField(max_length=100, null=True, blank=True)


class Chart(NamespaceAwareModel):
    id = models.AutoField(primary_key=True)
    tab = models.ForeignKey(Tab, on_delete=models.CASCADE, related_name="tab_charts")
    name = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    refresh_interval = models.CharField(max_length=100, null=True, blank=True)
    relative_window_time = models.CharField(max_length=100, null=True, blank=True)

class ChartItem(NamespaceAwareModel):
    id = models.AutoField(primary_key=True)
    chart = models.ForeignKey(Chart, on_delete=models.CASCADE, related_name="chart_items")
    source = models.CharField(max_length=100, null=True, blank=True)
    target = models.CharField(max_length=100, null=True, blank=True)
    split_by = models.CharField(max_length=100, null=True, blank=True)

class Filter(NamespaceAwareModel):
    id = models.AutoField(primary_key=True)
    chart_item = models.ForeignKey(ChartItem, on_delete=models.CASCADE, related_name="filters", null=True)
    operator = models.CharField(max_length=100, null=True, blank=True)
    key = models.CharField(max_length=100, null=True, blank=True)
    value = models.CharField(max_length=100, null=True, blank=True)