from django.db import models
from . import Asset


# class RelayAsset(Asset):
#     type = AssetType.SENSOR

class SwitchAsset(Asset):
    base_voltage = models.IntegerField(default=0)

# class Switch(Asset):
#     type = AssetType.DEVICE
#     # "name": "IS1.2",
#     # "base_voltage": "220",
#     # "buses": [
#     #     "_D517B484-1A4A-4B6E-9CA0-9E8281A57584",
#     #     "_3CDE0655-461F-4CDB-B462-6E09822FC5C0"
#     # ]


class LineAsset(Asset):
    base_voltage = models.FloatField(default=0)
    current_limit = models.FloatField(default=0)
    b0ch = models.FloatField(default=0)
    bch = models.FloatField(default=0)
    g0ch = models.FloatField(default=0)
    gch = models.FloatField(default=0)
    length = models.FloatField(default=0)
    r = models.FloatField(default=0)
    x = models.FloatField(default=0)
    x0 = models.FloatField(default=0)

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


class BusAsset(Asset):
    base_voltage = models.FloatField(default=0)
    line = models.ForeignKey(
        LineAsset, related_name="buses", on_delete=models.CASCADE)
    switch = models.ForeignKey(
        SwitchAsset, related_name="buses", on_delete=models.CASCADE)
    # region = models.CharField(max_length=100)
    # subregion = models.CharField(max_length=100)
    # substation = models.CharField(max_length=100)


class GeneratingUnitAsset(Asset):
    governor_SCD = models.FloatField(default=0)
    max_length = models.FloatField(default=0)
    maximum_allowable_spinning_reserve = models.FloatField(default=0)
    min_operating_P = models.FloatField(default=0)
    nominal_P = models.FloatField(default=0)
    normal_PF = models.FloatField(default=0)
    startup_cost = models.FloatField(default=0)
    variable_cost = models.FloatField(default=0)
#   "machines": {
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


class PowerTransformerTapChanger(models.Model):
    high_step = models.FloatField(default=0)
    low_step = models.FloatField(default=0)
    neutral_step = models.FloatField(default=0)
    neturalU = models.FloatField(default=0)
    step_voltage_increment = models.FloatField(default=0)
    tap_position = models.FloatField(default=0)


class PowerTransformerWinding(models.Model):
    base_voltage = models.FloatField()
    b = models.FloatField()
    b0 = models.FloatField()
    g = models.FloatField()
    g0 = models.FloatField()
    r = models.FloatField()
    r0 = models.FloatField()
    x = models.FloatField()
    x0 = models.FloatField()
    ratedS = models.FloatField()
    ratedU = models.FloatField()
    rground = models.FloatField()
    xground = models.FloatField()
    current_limit = models.FloatField()
    code_connect = models.CharField(max_length=10)
    type = models.CharField(max_length=10, default='primary')
    bus = models.ForeignKey(BusAsset, to_field="asset_ptr", db_column="bus",
                            related_name='windings', on_delete=models.DO_NOTHING)
    tap_changer = models.ForeignKey(
        PowerTransformerTapChanger, null=True, blank=True, on_delete=models.CASCADE)


class PowerTransformerAsset(Asset):
    windings = models.ManyToManyField(PowerTransformerWinding)


class LoadResponse(models.Model):
    exponent_model = models.BooleanField(default=True)
    p_constant_power = models.FloatField(null=True)
    p_constant_current = models.FloatField(null=True)
    p_constant_impedance = models.FloatField(null=True)
    q_constant_power = models.FloatField(null=True)
    q_constant_current = models.FloatField(null=True)
    q_constant_impedance = models.FloatField(null=True)


class PowerFlow(models.Model):
    p = models.IntegerField()
    q = models.IntegerField()


class LoadAsset(Asset):
    base_voltage = models.IntegerField(default=0)
    bus = models.ForeignKey(BusAsset, to_field="asset_ptr", db_column="bus",
                            related_name='loads', on_delete=models.DO_NOTHING)
    load_response = models.OneToOneField(
        LoadResponse, related_name="load", on_delete=models.CASCADE)
    power_flow = models.OneToOneField(
        PowerFlow, related_name="load", on_delete=models.CASCADE)

    # subregion = models.
    # substation = models.
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


class ShuntAsset(Asset):
    base_voltage = models.FloatField(default=0)
    b0_per_sections = models.FloatField(default=0)
    b_per_sections = models.FloatField(default=0)
    g0_per_sections = models.FloatField(default=0)
    g_per_sections = models.FloatField(default=0)
    max_sections = models.IntegerField(default=0)
    bus = models.ForeignKey(BusAsset, to_field="asset_ptr",
                            db_column="bus", related_name="shunts",
                            on_delete=models.DO_NOTHING)
    current_section = models.IntegerField(default=0)

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
