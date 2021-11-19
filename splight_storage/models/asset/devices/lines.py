from collections import namedtuple
from django.db import models
from .. import Asset

conductor_constants = namedtuple(
    "ConductorConstants",
    [
        "stranded",
        "high_rs",
        "diameter",
        "cross_section",
        "absortivity",
        "emmisivity",
        "materials_heat",
        "high_temperature",
        "low_temperature",
        "high_resistance",
        "low_resistance",
        "resistance",
        "static_capacity",
        "static_resitance",
    ],
)
heat_material = namedtuple(
    "HeatMaterial", ["name", "mass_per_unit_length",
                     "specific_heat_20deg", "beta"]
)


class LineAsset(Asset):
    class LineTypes(models.TextChoices):
        DRAKE = 'DRA', "drake"
        DOVE = 'DOV', "dove"

    __line_constants_by_type = {
        LineTypes.DRAKE: {
            "stranded": True,
            "high_rs": True,
            "diameter": 28.1e-3,
            "cross_section": None,
            "absortivity": 0.8,
            "emmisivity": 0.8,
            "materials_heat": [
                heat_material("steel", 0.5119, 481, 1.00e-4),
                heat_material("aluminum", 1.116, 897, 3.80e-4),
            ],
            "high_temperature": 75,
            "low_temperature": 25,
            "high_resistance": 8.688e-5,
            "low_resistance": 7.283e-5,
            "static_capacity": 300,
            "static_resitance": 8e-5,  # random value
        },
        LineTypes.DOVE: {
            "stranded": True,
            "high_rs": True,
            "diameter": 25.13e-3,
            "cross_section": None,
            "absortivity": 0.5,
            "emmisivity": 0.5,
            "materials_heat": [
                # heat_material("steel", 0.5119, 481, 1.00e-4),
                heat_material("aluminum", 1.116, 897, 3.80e-4),
            ],
            "high_temperature": 75,
            "low_temperature": 25,
            "high_resistance": 1.08e-4,
            "low_resistance": 8.95e-5,
            "static_capacity": 300,
            "static_resitance": 8e-5,  # random value
        }
    }

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
    buses = models.ManyToManyField('BusAsset', related_name='lines')  # BusAsset as string to avoid circular imports
    line_type = models.CharField(
        max_length=3, choices=LineTypes.choices, null=True)

    def get_constants(self):
        return conductor_constants(**self.__line_constants_by_type[self.line_type], resistance=self.resistance)

    def resistance(self, conductor_temp):
        const = self.get_constants()
        per_1 = (const.high_resistance - const.low_resistance) / \
            (const.high_temperature - const.low_temperature)
        return const.low_resistance + (conductor_temp - const.low_temperature) * per_1
