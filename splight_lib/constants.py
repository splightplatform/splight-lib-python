from collections import namedtuple


class LineConstants:
    __conductor_constants = namedtuple(
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
    __heat_material = namedtuple(
        "HeatMaterial", ["name", "mass_per_unit_length",
                         "specific_heat_20deg", "beta"]
    )
    __line_types = {
        "drake": {
            "stranded": True,
            "high_rs": True,
            "diameter": 28.1e-3,
            "cross_section": None,
            "absortivity": 0.8,
            "emmisivity": 0.8,
            "materials_heat": [
                __heat_material("steel", 0.5119, 481, 1.00e-4),
                __heat_material("aluminum", 1.116, 897, 3.80e-4),
            ],
            "high_temperature": 75,
            "low_temperature": 25,
            "high_resistance": 8.688e-5,
            "low_resistance": 7.283e-5,
            "static_capacity": 300,
            "static_resitance": 8e-5,  # random value
        },
        "dove": {
            "stranded": True,
            "high_rs": True,
            "diameter": 25.13e-3,
            "cross_section": None,
            "absortivity": 0.5,
            "emmisivity": 0.5,
            "materials_heat": [
                # __heat_material("steel", 0.5119, 481, 1.00e-4),
                __heat_material("aluminum", 1.116, 897, 3.80e-4),
            ],
            "high_temperature": 75,
            "low_temperature": 25,
            "high_resistance": 1.08e-4,
            "low_resistance": 8.95e-5,
            "static_capacity": 300,
            "static_resitance": 8e-5,  # random value
        }
    }

    def __init__(self, type_: str):
        try:
            self.constants = self.__conductor_constants(
                **self.__line_types[type_], resistance=self.resistance)
        except KeyError:
            return None

    def resistance(self, conductor_temperature):
        per_1 = (self.constants.high_resistance - self.constants.low_resistance) / \
            (self.constants.high_temperature - self.constants.low_temperature)
        return self.constants.low_resistance + (conductor_temperature - self.constants.low_temperature) * per_1
