from splight_lib import logging
from splight_storage.models.asset.base_asset import BaseAsset
from splight_storage.models.mapping.mappings import ResolvedClientMapping, ResolvedValueMapping
from splight_storage.models.mapping.mappings import ResolvedMapping
from typing import Dict, List
from datetime import datetime
from datetime import timedelta
from .utils import asset_filter, attributes_filter, time_range_filter
from .utils import get_match_timestamp_intervals_pipeline, Pipeline
from copy import deepcopy
from collections import defaultdict


logging = logging.getLogger(__name__)


def _get_interval_pipeline(asset_id: int,
                           from_: datetime,
                           to_: datetime,
                           interval_width: timedelta) -> Pipeline:
    """
    This function returns a pipeline that creates a list of documents with timestamp and asset_id
    that are regularly spaced in intervals of 5 seconds
    """

    intervals: List[Dict] = []
    for i in range(0, (to_ - from_).seconds // interval_width.seconds + 1):
        intervals.append({
            "asset_id": asset_id,
            "timestamp": from_ + i * interval_width,
        })

    return [
        {'$limit': 1},
        {
            '$project': {
                'default': {
                    '$const': intervals
                }
            }
        },
        {'$unwind': {'path': '$default'}},
        {'$replaceRoot': {'newRoot': '$default'}}
    ]


def _get_union_pipelines(mappings: List[ResolvedClientMapping],
                         original_asset_id: int,
                         from_: datetime,
                         to_: datetime) -> Pipeline:
    """
    This function returns a list of union steps that will retrive all the documents
    that match the asset_id and ref_attr in mappings, and will rename
    ref_attr to attr.
    For each unique asset_id in mappings there will be only one union step.

    :mappings: List[ResolvedClientMapping], mappings that have the stributes to be retrived
    :original_asset_id: int, id to update the asset_id field in the documents
    :param from_: datetime, the start time of the range
    :param to_: datetime, the end time of the range

    :return: Pipeline, the pipeline to get the values
    """

    grouped_mappings = defaultdict(list)

    for resolved_mapping in mappings:
        grouped_mappings[resolved_mapping.asset_id].append(resolved_mapping)

    pipelines: Pipeline = []

    for asset_id, mappings in grouped_mappings.items():
        attrs = [mapping.ref_attr for mapping in mappings]

        renames = {mapping.attr: f"${mapping.ref_attr}" for mapping in mappings}

        pipelines.append(
            {
                "$unionWith": {
                    "coll": "updates",
                    "pipeline": [
                        {"$match": {
                            **asset_filter(asset_id),
                            **attributes_filter(attrs),
                            **time_range_filter(from_, to_)
                        }
                        },
                        {
                            "$project": {
                                "timestamp": 1,
                                "asset_id": {"$const": original_asset_id},
                                **renames,
                            }
                        },
                    ],
                }
            }
        )

    return pipelines


def _get_group_pipeline(time_width: int = 5) -> Pipeline:
    """
    This function returns a step that grops the documents by asset_id and
    time intervals of 5 seconds, the it creates a cobined document whit all the
    attributes. if there are multiple aprearences of the same attibute in the
    time interval this pipeline does not guaranteed to retour always the same value.
    """
    return [
        {
            "$group": {
                "_id": "$timestamp",
                "item": {"$mergeObjects": "$$ROOT"},
            }
        },
        {"$replaceRoot": {"newRoot": "$item"}},
        {"$project": {"_id": 0}},
    ]


def _get_add_fields_pipeline(mappings: List[ResolvedClientMapping]):
    return [{
        "$addFields": {
            **{mapping.attr: {"value": mapping.value} for mapping in mappings}
        }
    }]


def _get_sort_pipeline():
    return [
        {
            "$sort": {
                "timestamp": -1
            }
        }
    ]


def get_asset_history_pipeline(asset: BaseAsset,
                               attributes: List[str],
                               from_: datetime,
                               to_: datetime,
                               interval: timedelta = timedelta(seconds=5)) -> Pipeline:
    """
    This pipeline is used to get the historic values of an asset attributes.
    If some attribute has a value and client mapping, this pipeline will
    return the value of the client mapping.

    :param asset: Asset, the asset to get the values
    :param attributes: List[str], the attributes to get the values if None all attributes will be used
    :param from_: datetime, the start time of the range
    :param to_: datetime, the end time of the range
    :param interval: timedelta, the interval of the time range

    :return: Pipeline, the pipeline to get the values
    """
    attributes = deepcopy(attributes)

    pipeline: Pipeline = []

    # Resolve maping to eather client o value mapping.
    resolved_attributes: List[ResolvedMapping] = asset.resolve_attributes(attributes)

    if len(attributes) != len(resolved_attributes):
        logging.warning(f"Some attributes are not mapped {attributes} {resolved_attributes}")

    pipeline.extend(_get_interval_pipeline(asset.id, from_, to_, interval))

    # Retrive attributes that resolve to client mapping
    resolver_client_mappings = [ra for ra in resolved_attributes if isinstance(ra, ResolvedClientMapping)]
    pipeline.extend(_get_union_pipelines(resolver_client_mappings,
                                         asset.pk,
                                         from_,
                                         to_))

    pipeline.extend(get_match_timestamp_intervals_pipeline(interval))

    # group and combine attributes.
    pipeline.extend(_get_group_pipeline())

    # Add attributes that have a value mapping.
    resolved_value_mappings = [ra for ra in resolved_attributes if isinstance(ra, ResolvedValueMapping)]
    pipeline.extend(_get_add_fields_pipeline(resolved_value_mappings))

    # Sort result in decending order
    pipeline.extend(_get_sort_pipeline())

    return pipeline
