from splight_models.constants import ComponentSize, RestartPolicy, LogginLevel, RunnerStatus
from splight_models.asset import Asset
from splight_models.attribute import Attribute
from splight_models.base import SplightBaseModel
from splight_models.datalake import RunnerDatalakeModel
from splight_models.graph import Graph
from splight_models.storage import StorageFile
from splight_models.rule import MappingRule

from datetime import datetime
from enum import Enum
from typing import Type, List, Dict, Tuple, Optional, Any, Union
from pydantic import BaseModel, create_model, Field
from copy import copy
from functools import cached_property
import inspect


class Parameter(SplightBaseModel):
    name: str
    description: str = ''
    type: str = "str"
    required: bool = False
    multiple: bool = False
    choices: Optional[List[Any]] = None
    depends_on: Optional[str] = None
    value: Any = None


class OutputParameter(SplightBaseModel):
    name: str
    description: str = ''
    type: str
    choices: Optional[List[Any]] = None
    depends_on: Optional[str] = None
    filterable: bool = False


class CustomType(SplightBaseModel):
    name: str
    fields: List[Parameter]


class Output(SplightBaseModel):
    name: str
    fields: List[OutputParameter]


class BaseRunner(SplightBaseModel):
    version: str  # Pointer to hub component
    custom_types: Optional[List[CustomType]] = []
    input: Optional[List[Parameter]] = []
    output: Optional[List[Output]] = []

    class Config:
        keep_untouched = (cached_property,)

    @cached_property
    def custom_types_model(self) -> Type:
        return RunnerModelFactory().get_custom_types_model(self.custom_types)

    @cached_property
    def input_model(self) -> Type:
        custom_type_model = self.custom_types_model
        custom_types = inspect.getmembers(custom_type_model)
        custom_types_dict = {a[0]: a[1] for a in custom_types if not a[0].startswith('__')}
        return RunnerModelFactory(custom_types_dict).get_input_model(self.input)

    @cached_property
    def output_model(self) -> Type:
        return RunnerModelFactory().get_output_model(self.output)


class Runner(BaseRunner):
    id: Optional[str]
    name: str
    description: Optional[str]
    log_level: LogginLevel = LogginLevel.info
    component_capacity: ComponentSize = ComponentSize.small
    restart_policy: RestartPolicy = RestartPolicy.ON_FAILURE
    status: RunnerStatus = RunnerStatus.STOPPED

    @property
    def collection(self):
        return 'default'


class Algorithm(Runner):
    @property
    def collection(self):
        return str(self.id)


class Network(Runner):
    @property
    def collection(self):
        return 'default'


class Connector(Runner):
    @property
    def collection(self):
        return 'default'


NATIVE_TYPES = {
    "int": int,
    "bool": bool,
    "str": str,
    "float": float,
    "Date": datetime,
}

DATABASE_TYPES = {
    "Asset": Asset,
    "Algorithm": Algorithm,
    "Attribute": Attribute,
    "Connector": Connector,
    "Graph": Graph,
    "Network": Network,
    "Rule": MappingRule,
}

STORAGE_TYPES = {
    "file": StorageFile,
}

SIMPLE_TYPES = list(NATIVE_TYPES.keys()) + list(DATABASE_TYPES.keys()) + list(STORAGE_TYPES.keys())


class RunnerModelFactory:
    def __init__(self, type_map: Dict[str, Type] = {}) -> None:
        self._type_map = {
            **type_map,
            **self._load_type_map()
        }

    @staticmethod
    def _load_type_map() -> Dict[str, Type]:
        type_map: Dict[str, Type] = {}
        type_map.update(NATIVE_TYPES)
        type_map.update({k: Union[str, v] for k, v in DATABASE_TYPES.items()})
        type_map.update({k: Union[str, v] for k, v in STORAGE_TYPES.items()})
        return type_map

    def get_custom_types_model(self, custom_types: List) -> Type:
        custom_types_dict: Dict[str, BaseModel] = {}

        for custom_type in custom_types:
            model = self._create_model(custom_type.name, custom_type.fields)
            custom_types_dict[custom_type.name] = model
            self._type_map[custom_type.name] = model

        return type("CustomTypes", (), custom_types_dict)

    def get_input_model(self, inputs: List) -> BaseModel:
        return self._create_model("Input", inputs)

    def get_output_model(self, outputs: List) -> BaseModel:
        output_models: Dict[str, BaseModel] = {}

        for output in outputs:
            output_format_field = {
                "output_format": Field(output.name, const=True),
            }
            output_models[output.name] = self._create_model(output.name,
                                                            output.fields,
                                                            output_format_field,
                                                            RunnerDatalakeModel)

        return type("Output", (), output_models)

    def _create_model(self,
                      name: str,
                      fields: List,
                      extra_fields: Dict = {},
                      base: Type = SplightBaseModel) -> Type:

        fields_dict: Dict[str, Tuple] = copy(extra_fields)
        for field in fields:
            type = self._type_map[field.type]
            choices = getattr(field, "choices", None)
            multiple = getattr(field, "multiple", False)
            required = getattr(field, "required", True)

            if choices:
                type = Enum(f"{field.name}-choices", {str(p): p for p in field.choices})

            if multiple:
                type = List[type]

            value = ...
            if not required:
                type = Optional[type]
                value = None

            fields_dict[field.name] = (type, value)

        return create_model(name, **fields_dict, __base__=base)
