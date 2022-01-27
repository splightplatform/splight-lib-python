from typing import Optional
from datetime import datetime
from .utils import time_range_filter
from .utils import Pipeline


def get_digital_offer_component_pipeline(from_: datetime, to_: datetime) -> Pipeline:
    pipeline = [{"$match": {**time_range_filter(from_, to_)}}]
    return pipeline
