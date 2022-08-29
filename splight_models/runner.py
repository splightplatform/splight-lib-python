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
from typing import Type, List, Dict, Tuple, Optional, Any
from pydantic import BaseModel, create_model, Field
from copy import copy


class Parameter(SplightBaseModel):
    name: str
    type: str = "str"
    required: bool = False
    multiple: bool = False
    choices: Optional[List[Any]] = None
    depends_on: Optional[str] = None
    value: Any = None


class OutputParameter(SplightBaseModel):
    name: str
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
    custom_types: List[CustomType] = []
    input: List[Parameter] = []
    output: List[Output] = []

    def get_modeled_instance(self) -> 'ModeledRunner':
        return ModeledRunnerFactory(self).get_modeled_runner()


class ModeledRunner(BaseRunner):
    custom_types: Type
    input: Type
    output: Type

    def get_modeled_instance(self) -> 'ModeledRunner':
        return self


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


class ModeledRunnerFactory:
    def __init__(self, runner: Runner) -> None:
        self.runner = runner
        self._type_map = self._load_type_map()

    def get_modeled_runner(self) -> ModeledRunner:
        data = self.runner.dict()
        data["custom_types"] = self._get_custom_types_model()
        data["input"] = self._get_input_model()
        data["output"] = self._get_output_model()
        return ModeledRunner(**data)

    def _load_type_map(self) -> Dict[str, Type]:
        type_map: Dict[str, Type] = {}
        type_map.update(NATIVE_TYPES)
        type_map.update(DATABASE_TYPES)
        type_map.update(STORAGE_TYPES)
        return type_map

    def _get_custom_types_model(self) -> Type:
        custom_types: Dict[str, BaseModel] = {}

        for custom_type in self.runner.custom_types:
            model = self._create_model(custom_type.name, custom_type.fields)
            custom_types[custom_type.name] = model
            self._type_map[custom_type.name] = model

        return type("CustomTypes", (), custom_types)

    def _get_input_model(self) -> BaseModel:
        return self._create_model("Input", self.runner.input)

    def _get_output_model(self) -> BaseModel:
        output_models: Dict[str, BaseModel] = {}

        for output in self.runner.output:
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
            required = getattr(field, "required", False)

            if choices:
                type = Enum(f"{field.name}-choices", {str(p): p for p in field.choices})

            if multiple:
                type = List[type]

            if not required:
                type = Optional[type]

            fields_dict[field.name] = (type, ...)

        return create_model(name, **fields_dict, __base__=base)
