from django.test import TestCase
from splight_database.django.djatabase.models.graph import *
from splight_database.django.djatabase.models.asset import Asset
from splight_models.exception import LockedGraphException, CrossGraphException


class TestGraph(TestCase):
    def setUp(self) -> None:
        self.graph1 = Graph.objects.create(title='Test Graph 1')
        self.graph2 = Graph.objects.create(title='Test Graph 2')
        self.locked_graph = Graph.objects.create(title='locked Graph', locked=True)
        self.asset1 = Asset.objects.create(name='Test Asset 1')
        self.asset2 = Asset.objects.create(name='Test Asset 2')
        self.asset3 = Asset.objects.create(name='Test Asset 3')

        return super().setUp()

    def test_create_node(self):
        node = Node.objects.create(
            type='test',
            graph=self.graph1,
            asset=self.asset1,
            color='red',
            fill_color='blue',
            position_x=1,
            position_y=2,
            width=3,
            height=4,
        )
        self.assertEqual(node.graph, self.graph1)

    def test_faile_create_node_locked_graph(self):
        with self.assertRaises(LockedGraphException):
            node = Node.objects.create(type='test', graph=self.locked_graph, asset=self.asset1)

    def test_create_edge(self):
        node1 = Node.objects.create(type='test', graph=self.graph1, asset=self.asset1)
        node2 = Node.objects.create(type='test', graph=self.graph1, asset=self.asset2)
        edge = Edge.objects.create(directed=False, graph=self.graph1, source=node1, target=node2, asset=self.asset3, source_handle='top', target_handle='right')
        self.assertEqual(edge.graph, self.graph1)

    def test_create_edge_without_asset(self):
        node1 = Node.objects.create(type='test', graph=self.graph1, asset=self.asset1)
        node2 = Node.objects.create(type='test', graph=self.graph1, asset=self.asset2)
        edge = Edge.objects.create(directed=False, graph=self.graph1, source=node1, target=node2, source_handle='top', target_handle='right')
        self.assertEqual(edge.graph, self.graph1)

    def test_fail_create_edge_locked_graph(self):
        node1 = Node.objects.create(type='test', graph=self.graph1, asset=self.asset1)
        node2 = Node.objects.create(type='test', graph=self.graph2, asset=self.asset2)
        with self.assertRaises(LockedGraphException):
            edge = Edge.objects.create(directed=False, graph=self.locked_graph, source=node1, target=node2, asset=self.asset3)

    def test_fail_create_edge_cross_graph(self):
        node1 = Node.objects.create(type='test', graph=self.graph1, asset=self.asset1)
        node2 = Node.objects.create(type='test', graph=self.graph2, asset=self.asset2)
        with self.assertRaises(CrossGraphException):
            edge = Edge.objects.create(directed=False, graph=self.graph1, source=node1, target=node2, asset=self.asset3)
