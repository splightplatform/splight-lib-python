from rest_framework import serializers
from models.asset import Asset
from models.asset.devices import *


class AssetSerializer(serializers.Serializer):
    class Meta:
        model = Asset
        fields = ['id', 'name']


class BusSerializer(AssetSerializer):
    class Meta:
        model = BusAsset
        fields = super.Meta.fields + ['__all__']


class LineSerializer(AssetSerializer):
    buses = BusSerializer(many=True)

    class Meta:
        model = LineAsset
        fields = super.Meta.fields + ['__all__']


class SwitchSerializer(AssetSerializer):
    buses = BusSerializer(many=True)

    class Meta:
        model = SwitchAsset
        fields = super.Meta.fields + ['__all__']


class PowerTransformerTapChangerSerializer(serializers.Serializer):
    class Meta:
        model = PowerTransformerTapChanger
        fields = ['__all__']


class PowerTransformerWindingSerializer(serializers.Serializer):
    tap_changer = PowerTransformerTapChangerSerializer()
    bus = BusSerializer()

    class Meta:
        model = PowerTransformerWinding
        fields = ['__all__']


class PowerTransformerSerializer(AssetSerializer):
    windings = PowerTransformerWindingSerializer(many=True)

    class Meta:
        model = PowerTransformerAsset
        fields = super.Meta.fields + ['__all__']


class LoadResponseSerializer(serializers.Serializer):
    class Meta:
        model = LoadResponse
        fields = ['__all__']


class PowerFlowSerializer(serializers.Serializer):
    class Meta:
        model = PowerFlow
        fields = ['__all__']


class LoadSerializer(AssetSerializer):
    bus = BusSerializer()
    load_response = LoadResponseSerializer()
    power_flow = PowerFlowSerializer()

    class Meta:
        model = LoadAsset
        fields = super.Meta.fields + ['__all__']


class ShuntSerializer(AssetSerializer):
    bus = BusSerializer()

    class Meta:
        model = ShuntAsset
        fields = super.Meta.fields + ['__all__']
