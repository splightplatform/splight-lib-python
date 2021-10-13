from django.db import models
from . import Asset


# class RelayAsset(Asset):
#     type = AssetType.SENSOR


# class BusAsset(Asset):
#     type = AssetType.DEVICE
#     # "name": "Te",
#     # "base_voltage": "13",
#     # "region": "Grid",
#     # "subregion": "DUMMY",
#     # "substation": "TERMINAL(2)"


# class LineAsset(Asset):
#     type = AssetType.DEVICE
#     # "name": "Line(1)",
#     # "type": "ACLineSegment",
#     # "base_voltage": "220",
#     # "current_limit": "2756",
#     # "b0ch": "0.00012",
#     # "bch": "0.00036",
#     # "g0ch": "0",
#     # "gch": "0",
#     # "length": "20",
#     # "r": "0.2",
#     # "r0": "2",
#     # "x": "2",
#     # "x0": "8",
#     # "buses": [
#     #     "_D517B484-1A4A-4B6E-9CA0-9E8281A57584",
#     #     "_EBDCA7E0-7FBC-4476-9CF4-EFA7996A6EC0"
#     # ]


# class GeneratingUnitAsset(Asset):
#     type = AssetType.DEVICE
#     # "type": "GeneratingUnit",
#     # "name": "Generador 1",
#     # "governor_SCD": "0",
#     # "max_operating_P": "9999",
#     # "maximum_allowable_spinning_reserve": "0",
#     # "min_operating_P": "0",
#     # "nominal_P": "320",
#     # "normal_PF": "1",
#     # "startup_cost": "0",
#     # "variable_cost": "0",
#     # "machines": {
#     #     "_7FAAE74C-7C1F-46D8-8481-8F82AC4BD729": {
#     #         "name": "Generador 1",
#     #         "type": "synchronous",
#     #         "maxQ": "400",
#     #         "minQ": "-400",
#     #         "qPercent": "100",
#     #         "r": "0",
#     #         "r0": "0",
#     #         "r2": "0",
#     #         "ratedS": "400",
#     #         "x": "0.845",
#     #         "x0": "0.04225",
#     #         "x2": "0.0845",
#     #         "bus": "_A18D288E-4927-4F7E-8848-8F2FC0BF95B6",
#     #         "powerflow": {
#     #             "p": "9.79233",
#     #             "q": "2.09433"
#     #         },
#     #         "base_voltage": "13",
#     #         "control_v": "1.03",
#     #         "regulated_bus": "_A18D288E-4927-4F7E-8848-8F2FC0BF95B6"
#     #     }


class PowerTransformerWinding(Asset):
    base_voltage = models.FloatField(null=True)
    b = models.FloatField(null=True)
    b0 = models.FloatField(null=True)
    g = models.FloatField(null=True)
    g0 = models.FloatField(null=True)
    r = models.FloatField(null=True)
    r0 = models.FloatField(null=True)
    x = models.FloatField(null=True)
    x0 = models.FloatField(null=True)
    ratedS = models.FloatField(null=True)
    ratedU = models.FloatField(null=True)
    rground = models.FloatField(null=True)
    xground = models.FloatField(null=True)
    bus = models.TextField(max_length=10, null=True)
    current_limit = models.FloatField(null=True)
    code_connect = models.FloatField(null=True)
    tap_changer = models.TextField(max_length=100, null=True)


class PowerTransformerTapChanger(Asset):
    
    def __init__(self, **kwargs) -> None:
        self.high_step = kwargs.get('high_step')
        self.low_step = kwargs.get('low_step')
        self.neutral_step = kwargs.get('neutral_step')
        self.neturalU = kwargs.get('neturalU')
        self.step_voltage_increment = kwargs.get('step_voltage_increment')
        self.tap_position = kwargs.get('tap_position')


class PowerTransformer(Asset):
    windings = models.ManyToManyField(PowerTransformerWinding)


# class Load(Asset):
#     type = AssetType.DEVICE
#     # "name": "General Load(1)",
#     # "bus": "_B753D49E-C08A-47C7-90FF-ABA9DF9704C6",
#     # "load_response": {
#     #     "exponent_model": "false",
#     #     "p_constant_power": "1.0",
#     #     "p_constant_current": "-",
#     #     "p_constant_impedance": "-",
#     #     "q_constant_power": "1.0",
#     #     "q_constant_current": "-",
#     #     "q_constant_impedance": "-"
#     # },
#     # "base_voltage": "13",
#     # "region": "Grid",
#     # "subregion": "GRID",
#     # "substation": "SINGLE BUSBAR",
#     # "powerflow": {
#     #     "p": "80",
#     #     "q": "30"
#     # }


# class Shunt(Asset):
#     type = AssetType.DEVICE
#     # "name": "SH1(1)",
#     # "base_voltage": "220",
#     # "b0_per_sections": "0",
#     # "b_per_sections": "0.000206612",
#     # "g0_per_sections": "0",
#     # "g_per_sections": "0",
#     # "max_sections": "1",
#     # "bus": "_2ADFBFB3-82BA-4689-AD12-FA86CBB3ABA8",
#     # "current_section": "1"


# class Switch(Asset):
#     type = AssetType.DEVICE
#     # "name": "IS1.2",
#     # "base_voltage": "220",
#     # "buses": [
#     #     "_D517B484-1A4A-4B6E-9CA0-9E8281A57584",
#     #     "_3CDE0655-461F-4CDB-B462-6E09822FC5C0"
#     # ]

