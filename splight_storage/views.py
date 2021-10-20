from rest_framework import viewsets, routers, status
from rest_framework.response import Response
from .models.asset import Asset
from .serializers import *
import splight_storage.models.asset.devices as devices


class AssetViewSet(viewsets.ModelViewSet):
    def create(self, request):
        data = request.data
        object = self.model.create(**data)
        object.save()
        content = self.serializer_class(object).data
        return Response(content, status=status.HTTP_201_CREATED)


class BusViewSet(AssetViewSet):
    model = BusAsset
    queryset = devices.BusAsset.objects.all()
    serializer_class = BusSerializer


class ConnectedViewSet(AssetViewSet):
    related_objects = []

    def retrive_related_objects_data(self, data):
        related_objects_data = {}
        for obj in self.related_objects:
            id = data.pop(obj['name'])
            related_objects_data[obj['name']] = obj['model'].get_by_id(id)
        return related_objects_data

    def create(self, request):
        data = request.data
        related_objects_data = self.retrive_related_objects_data(data)
        data.update(related_objects_data)
        object = self.model.create(**data)
        content = self.serializer_class(object).data
        return Response(content, status=status.HTTP_201_CREATED)


class NestedViewSet(AssetViewSet):

    # children = List(child)
    # child = {
    #   name:str,
    #   model: Model,
    #   related_name: str
    # }
    # children_data = Dict(str,List(child_data))
    # child_data depends on subclass

    children = []

    def retrieve_child_object(self, child, child_data):
        return None

    def retrieve_children_data(self, data):
        children_dataset = {}
        for child in self.children:
            try:
                child_data = data.pop(child['name'])
            except KeyError:
                return Response({'detail': 'Key not found : ' + child['name']},
                                status=status.HTTP_400_BAD_REQUEST)
            children_dataset[child['name']] = child_data
        return children_dataset

    def process_children(self, children_data, object):
        for child in self.children:
            child_set = getattr(object, child['name'])
            for c_data in children_data[child['name']]:
                child_object = self.retrieve_child_object(child, c_data)
                child_set.add(child_object)
                child_object.save()

    def create(self, request):
        data = request.data
        children_data = self.retrieve_children_data(data)
        object = self.model.create(**data)
        self.process_children(children_data, object)
        object.save()
        content = self.serializer_class(object).data
        return Response(content, status=status.HTTP_201_CREATED)


class IdNestedViewSet(NestedViewSet):
    # child_data = List(Ids)
    def retrieve_child_object(self, child, c_id):
        return child['model'].get_by_id(c_id)


class DataNestedViewSet(NestedViewSet):
    # child_data = List(Dict)
    def retrieve_child_object(self, child, c_data):
        return child['model'].create(**c_data)


class LineViewSet(IdNestedViewSet):
    model = devices.LineAsset
    children = [
        {'name': 'buses', 'model': devices.BusAsset,
            'related_name': 'line'}
    ]
    queryset = devices.LineAsset.objects.all()
    serializer_class = LineSerializer


class SwitchViewSet(IdNestedViewSet):
    model = devices.SwitchAsset
    children = [
        {'name': 'buses', 'model': devices.BusAsset,
            'related_name': 'switch'}
    ]
    queryset = devices.SwitchAsset.objects.all()
    serializer_class = SwitchSerializer


class PowerTransformerViewSet(DataNestedViewSet):
    model = devices.PowerTransformerAsset
    children = [
        {'name': 'windings', 'model': devices.PowerTransformerWinding,
            'related_name': 'transformer'}
    ]
    queryset = devices.PowerTransformerAsset.objects.all()
    serializer_class = PowerTransformerSerializer


class GeneratingUnitViewSet(viewsets.ModelViewSet):
    model = devices.GeneratingUnitAsset
    queryset = devices.GeneratingUnitAsset.objects.all()
    serializer_class = GeneratingUnitSerializer


class LoadViewSet(viewsets.ModelViewSet):
    model = devices.LoadAsset
    queryset = devices.LoadAsset.objects.all()
    serializer_class = LoadSerializer


class ShuntViewSet(ConnectedViewSet):
    model = devices.ShuntAsset
    related_objects = [{'name': 'bus', 'model': devices.BusAsset}]
    queryset = devices.ShuntAsset.objects.all()
    serializer_class = ShuntSerializer


asset_router = routers.DefaultRouter()
asset_router.register(r'buses', BusViewSet)
asset_router.register(r'lines', LineViewSet)
asset_router.register(r'switches', SwitchViewSet)
asset_router.register(r'transformers', PowerTransformerViewSet)
asset_router.register(r'generating_units', GeneratingUnitViewSet)
asset_router.register(r'loads', LoadViewSet)
asset_router.register(r'shunts', ShuntViewSet)
