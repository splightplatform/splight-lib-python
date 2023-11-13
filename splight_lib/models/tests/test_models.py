import json
import pytest
from pathlib import Path
from typing import Dict

from splight_lib.models import HubComponent, Asset


@pytest.fixture()
def example_models():
    directory_name = Path(__file__).absolute().parent
    with open(directory_name / "models.json", "r") as fid:
        all_data = json.load(fid)
    return all_data


def test_asset_model(example_models: Dict):
    assets_raw = example_models["assets"]
    _ = [Asset.model_validate(asset_def) for asset_def in assets_raw]


def test_hub_component(example_models: Dict):
    raw_data = example_models["hub_components"]
    _ = [HubComponent.model_validate(item) for item in raw_data]
