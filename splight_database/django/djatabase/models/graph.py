from django.db import models
from .namespace import NamespaceAwareModel
from splight_models.exception import LockedGraphException, CrossGraphException


class Graph(NamespaceAwareModel):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)
    locked = models.BooleanField(default=False)


class Node(NamespaceAwareModel):
    type = models.CharField(max_length=100)
    color = models.CharField(max_length=100, default=None, null=True)
    position_y = models.IntegerField(default=0)
    position_x = models.IntegerField(default=0)
    width = models.CharField(max_length=50, null=True, blank=True)
    height = models.CharField(max_length=50, null=True, blank=True)
    handle_orientation = models.CharField(max_length=100, default=None, null=True)

    graph = models.ForeignKey(Graph, on_delete=models.CASCADE, related_name='nodes')
    asset = models.ForeignKey('Asset', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.graph.locked:
            raise LockedGraphException()

        super().save(*args, **kwargs)


class Edge(NamespaceAwareModel):
    directed = models.BooleanField(default=False)

    graph = models.ForeignKey(Graph, on_delete=models.CASCADE, related_name='edges')
    asset = models.ForeignKey('Asset', on_delete=models.CASCADE, default=None)
    source = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='outgoing_edges')
    target = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='incoming_edges')
    color = models.CharField(max_length=100, default=None, null=True)

    def save(self, *args, **kwargs):
        if self.graph.locked:
            raise LockedGraphException()

        if not self.source.graph == self.graph:
            raise CrossGraphException()

        if not self.target.graph == self.graph:
            raise CrossGraphException()

        super().save(*args, **kwargs)
