from django.db import models
from .namespace import NamespaceAwareModel


class UnmodifiableGraphException(Exception):
    pass


class CrossGraphException(Exception):
    pass


class Graph(NamespaceAwareModel):
    title = models.CharField(max_length=100)
    modifiable = models.BooleanField(default=True)


class Node(NamespaceAwareModel):
    type = models.CharField(max_length=100)

    graph = models.ForeignKey(Graph, on_delete=models.CASCADE, related_name='nodes')
    asset = models.ForeignKey('Asset', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.graph.modifiable:
            raise UnmodifiableGraphException()

        super().save(*args, **kwargs)


class Edge(NamespaceAwareModel):
    directed = models.BooleanField(default=False)

    graph = models.ForeignKey(Graph, on_delete=models.CASCADE, related_name='edges')
    source = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='outgoing_edges')
    target = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='incoming_edges')

    def save(self, *args, **kwargs):
        if not self.graph.modifiable:
            raise UnmodifiableGraphException()

        if not self.source.graph == self.graph:
            raise CrossGraphException()

        if not self.target.graph == self.graph:
            raise CrossGraphException()

        super().save(*args, **kwargs)
