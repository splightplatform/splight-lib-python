from django.db.models import fields
from rest_framework import serializers
from .models.asset import Asset
from .models.asset.devices import *


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['id', 'name', 'type']


class BusSerializer(AssetSerializer):
    class Meta:
        model = BusAsset
        fields = AssetSerializer.Meta.fields + ['base_voltage']


class LineSerializer(AssetSerializer):
    buses = BusSerializer(many=True)

    class Meta:
        model = LineAsset
        fields = AssetSerializer.Meta.fields + \
            ['base_voltage', 'current_limit', 'b0ch', 'bch',
                'g0ch', 'gch', 'r', 'x', 'x0', 'buses']

    def create(self, validated_data):
        buses_data = validated_data.pop('buses')
        line = LineAsset.create(**validated_data)
        line.buses = BusAsset.objects.filter(id__in=buses_data)
        return line


class SwitchSerializer(AssetSerializer):
    buses = BusSerializer(many=True)

    class Meta:
        model = SwitchAsset
        fields = AssetSerializer.Meta.fields + ['base_voltage', 'buses']


class PowerTransformerTapChangerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PowerTransformerTapChanger
        fields = '__all__'


class PowerTransformerWindingSerializer(serializers.ModelSerializer):
    tap_changer = PowerTransformerTapChangerSerializer()
    bus = BusSerializer()

    class Meta:
        model = PowerTransformerWinding
        fields = '__all__'


class PowerTransformerSerializer(AssetSerializer):
    windings = PowerTransformerWindingSerializer(many=True)

    class Meta:
        model = PowerTransformerAsset
        fields = AssetSerializer.Meta.fields + ['windings']


class PowerFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = PowerFlow
        fields = '__all__'


class MachineSerializer(AssetSerializer):
    bus = BusSerializer()
    regulated_bus = BusSerializer()
    power_flow = PowerFlowSerializer()

    class Meta:
        models = MachineAsset
        fields = AssetSerializer.Meta.fields + \
            ['bus', 'regulated_bus', 'power_flow']


class GeneratingUnitSerializer(AssetSerializer):
    machines = MachineSerializer(many=True)

    class Meta:
        models = GeneratingUnitAsset
        fields = AssetSerializer.Meta.fields + \
            ['governor_SCD', 'max_length', 'maximum_allowable_spinning_reserve',
                'min_operating_P', 'nominal_P', 'normal_PF', 'startup_cost', 'variable_cost']


class LoadResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoadResponse
        fields = '__all__'


class LoadSerializer(AssetSerializer):
    bus = BusSerializer()
    load_response = LoadResponseSerializer()
    power_flow = PowerFlowSerializer()

    class Meta:
        model = LoadAsset
        fields = AssetSerializer.Meta.fields + \
            ['base_voltage', 'bus', 'load_response', 'power_flow']


class ShuntSerializer(AssetSerializer):
    bus = BusSerializer()

    class Meta:
        model = ShuntAsset
        fields = AssetSerializer.Meta.fields + ['base_voltage', 'b0_per_sections', 'b_per_sections',
                                                'g0_per_sections', 'g_per_sections', 'max_sections', 'bus', 'current_section']
