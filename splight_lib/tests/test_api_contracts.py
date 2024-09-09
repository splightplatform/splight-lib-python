import json
import os
import random
import uuid
from collections import namedtuple
from typing import Any, Dict

import jsonref
import requests
import yaml
from geojson_pydantic import GeometryCollection
from openapi_schema_validator import validate
from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory

from splight_lib.models import (
    Asset,
    Attribute,
    Function,
    Metadata,
    RoutineObject,
    Secret,
)
from splight_lib.models.component import InputDataAddress, InputParameter
from splight_lib.models.data_address import DataAddresses
from splight_lib.models.function import FunctionItem

ASSET_METADATA_SET = [
    Metadata(
        id=str(uuid.uuid4()),
        name="metadata0",
        type="Number",
        value=1,
    ),
    Metadata(
        id=str(uuid.uuid4()),
        name="metadata1",
        type="Number",
        value=0.4,
    ),
    Metadata(
        id=str(uuid.uuid4()),
        name="metadata2",
        type="Boolean",
        value=True,
    ),
    Metadata(
        id=str(uuid.uuid4()),
        name="metadata3",
        type="String",
        value="value",
    ),
]

CONFIG_PARAM = InputParameter(
    name="parameter",
    value=10,
    type="float",
)

with open(
    os.path.join(os.getcwd(), "splight_lib/tests/asset_geometries.json"), "r"
) as fid:
    GEOMETRIES = json.load(fid)
GEOMETRIES.insert(0, None)


class GeometryCollectionFactory(ModelFactory[GeometryCollection]):
    pass


class AttributeFactory(ModelFactory[Attribute]):
    id: str = Use(lambda: str(uuid.uuid4()))
    asset: str = Use(lambda: str(uuid.uuid4()))
    unit: str = Use(lambda: random.choice(["m", "cm", "mm"]))
    type: str = Use(lambda: random.choice(["Number", "String", "Boolean"]))


class AssetFactory(ModelFactory[Asset]):
    id: str = Use(lambda: str(uuid.uuid4()))
    metadata = ASSET_METADATA_SET
    attributes = AttributeFactory.batch(random.randint(1, 10))
    geometry = Use(lambda: GEOMETRIES[random.randint(0, len(GEOMETRIES) - 1)])
    related_assets = []


class FunctionItemFactory(ModelFactory[FunctionItem]):
    id = Use(lambda: str(uuid.uuid4()))
    query_filter_asset = Use(
        lambda: {"id": str(uuid.uuid4()), "name": "asset"}
    )
    query_filter_attribute = Use(
        lambda: {
            "id": str(uuid.uuid4()),
            "name": "attribute",
            "type": "Number",
        }
    )


class FunctionFactory(ModelFactory[Function]):
    __allow_none_optionals__ = False

    id: str = Use(lambda: str(uuid.uuid4()))
    type = "cron"

    target_variable = "Z"
    target_asset = AssetFactory.build().model_dump()
    target_attribute = AttributeFactory.build().model_dump()

    function_items = FunctionItemFactory.batch(random.randint(1, 10))


class DataAddressesFactory(ModelFactory[DataAddresses]):
    asset = Use(lambda: str(uuid.uuid4()))
    attribute = Use(lambda: str(uuid.uuid4()))
    type = None


class InputDataAddressFactory(ModelFactory[InputDataAddress]):
    value = Use(DataAddressesFactory.batch, size=1)


class RoutineObjectFactory(ModelFactory[RoutineObject]):
    id: str = Use(lambda: str(uuid.uuid4()))
    config = [CONFIG_PARAM]
    input = Use(InputDataAddressFactory.batch, size=2)
    output = Use(InputDataAddressFactory.batch, size=2)
    component_id = Use(lambda: str(uuid.uuid4()))


class SecretFactory(ModelFactory[Secret]):
    id: str = Use(lambda: str(uuid.uuid4()))


ModelMapping = namedtuple("ModelMapping", ["factory", "schema"])

MODEL_MAPPING = {
    "Attribute": ModelMapping(AttributeFactory, "AssetAttribute"),
    "Asset": ModelMapping(AssetFactory, "Asset"),
    "Function": ModelMapping(FunctionFactory, "Function"),
    "RoutineObject": ModelMapping(RoutineObjectFactory, "RoutineObject"),
    "Secret": ModelMapping(SecretFactory, "Secret"),
    # TODO: Include File and Component
}


def read_swagger(url: str) -> Dict[str, Any]:
    response = requests.get(url)
    return yaml.safe_load(response.text)


def test_api_contract():
    api_url = os.getenv(
        "SPLIGHT_PLATFORM_API_HOST", "https://integrationapi.splight-ai.com"
    )
    url = f"{api_url}/schema/"
    data = read_swagger(url)

    # Replace all reference defined by $ref
    data = jsonref.loads(json.dumps(data))
    models_def = data["components"]["schemas"]

    for model_name in MODEL_MAPPING:
        mapping = MODEL_MAPPING[model_name]
        factory = mapping.factory
        schema_name = mapping.schema
        print(f"Validating model {model_name}")
        instances = factory.batch(random.randint(10, 30))
        model_schema = models_def[schema_name]

        # TODO: Key config should not be excluded, this is because
        # for RoutineObject, the config is a JSON field and the
        # validation fails
        _ = [
            validate(
                instance=item.model_dump(exclude={"config"}),
                schema=model_schema,
            )
            for item in instances
        ]
