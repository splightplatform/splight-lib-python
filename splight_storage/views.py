from rest_framework import viewsets, routers, status
from rest_framework.response import Response
from .models.asset import Asset
from .serializers import *
import splight_storage.models.asset.devices as devices


class AssetViewSet(viewsets.ModelViewSet):
    def delete(self, request, object_id):
        print("hello")
        try:
            object = self.model.get_by_id(object_id)
        except KeyError:
            return Response({'detail': 'Invalid Id'}, status=status.HTTP_400_BAD_REQUEST)
        object.delete()
        return Response({'detail': 'Succefuly deleted'}, status=status.HTTP_200_OK)


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
    children = []

    def retrieve_children_data(self, data):
        children_ids = {}
        for child in self.children:
            try:
                child_data = data.pop(child['name'])
            except KeyError:
                return Response({'detail': 'Key not found : ' + child['name']},
                                status=status.HTTP_400_BAD_REQUEST)
            children_ids[child['name']] = child_data
        return children_ids

    def process_children(self, c_data, obj):
        pass

    def create(self, request):
        data = request.data
        children_data = self.retrieve_children_data(data)
        object = self.model.create(**data)
        self.process_children(children_data, object)
        object.save()
        content = self.serializer_class(object).data
        return Response(content, status=status.HTTP_201_CREATED)


class IdNestedViewSet(NestedViewSet):

    def process_children(self, children_data, object):
        for child in self.children:
            child_set = getattr(object, child['name'])
            for c_id in children_data[child['name']]:
                child_object = child['model'].get_by_id(c_id)
                child_set.add(child_object)
                child_object.save()


class DataNestedViewSet(NestedViewSet):
    def process_children(self, children_data, object):
        for child in self.children:
            for c in children_data[child['name']]:
                child_object = child['model'].create(**c)
                related_set = getattr(child_object, child['related_name'])
                related_set.add(object)
                child_object.save()


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
            'related_name': 'transformers'}
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
