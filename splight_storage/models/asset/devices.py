from django.db import models
from . import Asset


class BusAsset(Asset):
    base_voltage = models.FloatField(default=0)


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
    buses = models.ManyToManyField(BusAsset, related_name='lines')


class SwitchAsset(Asset):
    base_voltage = models.IntegerField(default=0)
    buses = models.ManyToManyField(BusAsset, related_name='switches')


class PowerTransformerAsset(Asset):
    pass


class PowerTransformerTapChanger(models.Model):
    high_step = models.FloatField(default=0)
    low_step = models.FloatField(default=0)
    neutral_step = models.FloatField(default=0)
    neturalU = models.FloatField(default=0)
    step_voltage_increment = models.FloatField(default=0)
    tap_position = models.FloatField(default=0)


class PowerTransformerWinding(models.Model):
    base_voltage = models.FloatField(default=0)
    b = models.FloatField(default=0)
    b0 = models.FloatField(default=0)
    g = models.FloatField(default=0)
    g0 = models.FloatField(default=0)
    r = models.FloatField(default=0)
    r0 = models.FloatField(default=0)
    x = models.FloatField(default=0)
    x0 = models.FloatField(default=0)
    ratedS = models.FloatField(default=0)
    ratedU = models.FloatField(default=0)
    rground = models.FloatField(default=0)
    xground = models.FloatField(default=0)
    current_limit = models.FloatField(default=0)
    code_connect = models.CharField(max_length=10, default="NA")
    type = models.CharField(max_length=10, default='primary')
    transformer = models.ForeignKey(
        PowerTransformerAsset, to_field="asset_ptr",
        db_column="transformer", related_name="windings",
        on_delete=models.CASCADE, null=True)
    bus = models.ForeignKey(BusAsset, to_field="asset_ptr",
                            db_column="bus", related_name='windings',
                            on_delete=models.SET_NULL, null=True)
    tap_changer = models.ForeignKey(
        PowerTransformerTapChanger, null=True,
        blank=True, on_delete=models.CASCADE)


class PowerFlow(models.Model):
    p = models.FloatField(default=0)
    q = models.FloatField(default=0)


class GeneratingUnitAsset(Asset):
    governor_SCD = models.FloatField(default=0)
    max_length = models.FloatField(default=0)
    maximum_allowable_spinning_reserve = models.FloatField(default=0)
    min_operating_P = models.FloatField(default=0)
    nominal_P = models.FloatField(default=0)
    normal_PF = models.FloatField(default=0)
    startup_cost = models.FloatField(default=0)
    variable_cost = models.FloatField(default=0)


class Machine(models.Model):
    name = models.CharField(max_length=100, default="")
    machine_type = models.CharField(max_length=100)
    maxQ = models.FloatField(default=0)
    minQ = models.FloatField(default=0)
    qPercent = models.IntegerField(default=0)
    r = models.FloatField(default=0)
    r0 = models.FloatField(default=0)
    r2 = models.FloatField(default=0)
    rared = models.FloatField(default=0)
    x = models.FloatField(default=0)
    x0 = models.FloatField(default=0)
    x2 = models.FloatField(default=0)
    bus = models.ForeignKey(
        BusAsset, to_field="asset_ptr",
        db_column="bus", related_name='machines',
        on_delete=models.SET_NULL, null=True, blank=True)
    regulated_bus = models.ForeignKey(
        BusAsset, to_field="asset_ptr",
        db_column="regulated_bus", related_name='regulated_machines',
        on_delete=models.SET_NULL, null=True, blank=True)
    power_flow = models.OneToOneField(
        PowerFlow, related_name="machine",
        on_delete=models.CASCADE, null=True)
    base_voltage = models.FloatField(default=0)
    control_v = models.FloatField(default=0)
    generating_unit = models.ForeignKey(
        GeneratingUnitAsset, to_field="asset_ptr",
        db_column="generating_unit", related_name="machines",
        on_delete=models.CASCADE)


class LoadResponse(models.Model):
    exponent_model = models.BooleanField(default=True)
    p_constant_power = models.FloatField(null=True)
    p_constant_current = models.FloatField(null=True)
    p_constant_impedance = models.FloatField(null=True)
    q_constant_power = models.FloatField(null=True)
    q_constant_current = models.FloatField(null=True)
    q_constant_impedance = models.FloatField(null=True)


class LoadAsset(Asset):
    base_voltage = models.IntegerField(default=0)
    bus = models.ForeignKey(
        BusAsset, to_field="asset_ptr", db_column="bus",
        related_name='loads', on_delete=models.CASCADE)
    load_response = models.OneToOneField(
        LoadResponse, related_name="load",
        on_delete=models.CASCADE)
    power_flow = models.OneToOneField(
        PowerFlow, related_name="load",
        on_delete=models.CASCADE, null=True)


class ShuntAsset(Asset):
    base_voltage = models.FloatField(default=0)
    b0_per_sections = models.FloatField(default=0)
    b_per_sections = models.FloatField(default=0)
    g0_per_sections = models.FloatField(default=0)
    g_per_sections = models.FloatField(default=0)
    max_sections = models.IntegerField(default=0)
    bus = models.ForeignKey(BusAsset, to_field="asset_ptr",
                            db_column="bus", related_name="shunts",
                            on_delete=models.DO_NOTHING,
                            null=True)
    current_section = models.IntegerField(default=0)
