from rest_framework import viewsets, routers
from .models.asset import Asset
from .serializers import *
import splight_storage.models.asset.devices as devices


class BusViewSet(viewsets.ModelViewSet):
    queryset = devices.BusAsset.objects.all()
    serializer_class = BusSerializer


class LineViewSet(viewsets.ModelViewSet):
    queryset = devices.LineAsset.objects.all()
    serializer_class = LineSerializer


class SwitchViewSet(viewsets.ModelViewSet):
    queryset = devices.SwitchAsset.objects.all()
    serializer_class = SwitchSerializer


class PowerTransformerViewSet(viewsets.ModelViewSet):
    queryset = devices.PowerTransformerAsset.objects.all()
    serializer_class = PowerTransformerSerializer


class GeneratingUnitViewSet(viewsets.ModelViewSet):
    queryset = devices.GeneratingUnitAsset.objects.all()
    serializer_class = GeneratingUnitSerializer


class LoadViewSet(viewsets.ModelViewSet):
    queryset = devices.LoadAsset.objects.all()
    serializer_class = LoadSerializer


class ShuntViewSet(viewsets.ModelViewSet):
    queryset = devices.ShuntAsset.objects.all()
    serializer_class = ShuntSerializer


asset_router = routers.DefaultRouter()
asset_router.register('buses', BusViewSet)
asset_router.register('lines', LineViewSet)
asset_router.register('switches', SwitchViewSet)
asset_router.register('transformers', PowerTransformerViewSet)
asset_router.register('generating_units', GeneratingUnitViewSet)
asset_router.register('loads', LoadViewSet)
asset_router.register('shunts', ShuntViewSet)
