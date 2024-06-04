from collections import namedtuple
from typing import NamedTuple, Optional

from pydantic import Field, computed_field

from splight_lib.models.asset import Asset
from splight_lib.models.base import SplightDatabaseBaseModel
from splight_lib.models.exceptions import (
    InvalidArgument,
    InvalidConfigType,
    InvalidResourceType,
    MissingAsset,
)
from splight_lib.models.hub_solution import HubSolution

CAST_TO = {
    "int": int,
    "float": float,
    "bool": bool,
    "str": str,
}


def get_model_class(config: list[dict], name: str) -> NamedTuple:
    config_class = namedtuple(name, [x.name for x in config])
    return config_class


def load_solution_config(
    config: list[dict], config_class: NamedTuple
) -> NamedTuple:
    config_dict = {}
    for item in config:
        if item["type"] not in CAST_TO:
            raise InvalidConfigType(item["name"], item["type"])
        if item["multiple"]:
            value = [CAST_TO[item["type"]](x) for x in item["value"]]
        else:
            value = CAST_TO[item["type"]](item["value"])
        config_dict.update({item["name"]: value})
    config = config_class(**config_dict)
    return config


def load_solution_resources(
    resources: list[dict], model_class: NamedTuple
) -> namedtuple:
    resources_dict = {}
    for resource in resources:
        if type_ := resource["type"] != "Asset":
            raise InvalidResourceType(resource["name"], type_)
        if not resource["value"]:
            raise MissingAsset(resource["name"])

        if resource["multiple"]:
            value = [Asset.retrieve(x) for x in resource["value"]]
        else:
            value = Asset.retrieve(resource["value"])
        resources_dict.update({resource["name"]: value})
    resources = model_class(**resources_dict)
    return resources


# class Solution(BaseModel):
#     id: str
#     name: str
#     description: str
#     hub_solution: HubSolution
#
#     @classmethod
#     def list(cls) -> list[Self]:
#         return [solution.parse() for solution in RawSolution.list()]
#
#     @classmethod
#     def retrieve(cls, solution_id: str) -> Self:
#         return RawSolution.retrieve(solution_id).parse()


class Solution(SplightDatabaseBaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    hub_solution: HubSolution
    raw_config: list[dict] = Field(alias="config")
    raw_resources: list[dict] = Field(alias="resources")

    def model_dump(self, *args, **kwargs):
        kwargs.update({"by_alias": True})
        return super().model_dump(*args, **kwargs)

    def model_dump_json(self, *args, **kwargs):
        kwargs.update({"by_alias": True})
        return super().model_dump_json(*args, **kwargs)

    @computed_field(alias="parsed_config")
    @property
    def config(self) -> NamedTuple:
        model_class = get_model_class(self.hub_solution.config, "Config")
        config = load_solution_config(self.raw_config, model_class)
        return config

    @computed_field(alias="parsed_resources")
    @property
    def resources(self) -> NamedTuple:
        model_class = get_model_class(self.hub_solution.resources, "Resources")
        resources = load_solution_resources(self.raw_resources, model_class)
        return resources

    def update_config(self, **kwargs: dict):
        valid_params = [x["name"] for x in self.raw_config]
        for key, value in kwargs.items():
            if key not in valid_params:
                raise InvalidArgument(
                    (
                        f"Got invalid parameter {key}. Valid config parameter "
                        f"are {valid_params}"
                    )
                )
            for item in self.raw_config:
                if item["name"] == key:
                    item["value"] = value
                    break

    def update_resources(self, **kwargs: dict):
        valid_params = [x["name"] for x in self.raw_resources]
        for key, value in kwargs.items():
            if key not in valid_params:
                raise InvalidArgument(
                    (
                        f"Got invalid parameter {key}. Valid resource "
                        f"parameter are {valid_params}"
                    )
                )
            for item in self.raw_resources:
                if item["name"] == key:
                    item["value"] = value
                    break

    # def parse(self) -> Solution:
    #     config = load_solution_config(self.config)
    #     config_type = NamedTuple(
    #         "Config", [(x["name"], Any) for x in self.config]
    #     )
    #     resources = load_solution_resources(self.resources)
    #     resouces_type = NamedTuple(
    #         "Resources", [(x["name"], Any) for x in self.resources]
    #     )
    #     model = create_model(
    #         "Solution",
    #         __base__=Solution,
    #         config=(config_type, ...),
    #         resources=(resouces_type, ...),
    #     )
    #     return model(
    #         id=self.id,
    #         name=self.name,
    #         description=self.description,
    #         hub_solution=self.hub_solution,
    #         config=config,
    #         resources=resources,
    #     )
