import json
import os
from datetime import timedelta, timezone
from functools import partial
from typing import Dict, List, Type, Union

import pandas as pd
from splight_abstract.client import QuerySet
from splight_abstract.datalake import AbstractDatalakeClient
from splight_lib.client.file_handler import FixedLineNumberFileHandler
from splight_lib.client.filter import value_filter
from splight_lib.logging._internal import LogTags, get_splight_logger
from splight_models import DatalakeModel, Query

DLResource = Type[DatalakeModel]

logger = get_splight_logger()


class LocalDatalakeClient(AbstractDatalakeClient):
    """Datalake client implementation for a storing locally documents
    in different files.
    """

    _DEFAULT = "default"
    _PREFIX = "dl_"
    _TOTAL_DOCS = 10000

    def __init__(self, namespace: str, path: str):
        super().__init__(namespace=namespace)
        self._base_path = path
        logger.info(
            "Local datalake client initialized.", tags=LogTags.DATALAKE
        )

    def _raw_get(
        self,
        resource_type: DLResource,
        limit_: int = 1000,
        skip_: int = 0,
        sort: Union[List, str] = ["timestamp__desc"],
        group_id: Union[List, str] = [],
        group_fields: Union[List, str] = [],
        tzinfo: timezone = timezone(timedelta()),
        **kwargs,
    ) -> List[DLResource]:
        collection = resource_type.Meta.collection_name
        file_path = os.path.join(
            self._base_path, self._get_file_name(collection)
        )
        handler = FixedLineNumberFileHandler(
            file_path=file_path, total_lines=self._TOTAL_DOCS
        )
        documents = [json.loads(doc) for doc in handler.read()]

        filters = kwargs
        filters.update({"output_format": resource_type.__name__})
        documents = self._filter(documents, filters=filters)

        reverse = False
        if "__desc" not in sort:
            reverse = True
        documents.sort(key=lambda x: x["timestamp"], reverse=reverse)

        # TODO: review how to apply grouping
        return [
            resource_type.parse_obj(doc)
            for doc in documents[skip_ : limit_ + 1]
        ]

    def get(
        self,
        resource_type: Type,
        limit_: int = 50,
        skip_: int = 0,
        sort: Union[List, str] = ["timestamp__desc"],
        group_id: Union[List, str] = [],
        group_fields: Union[List, str] = [],
        tzinfo: timezone = timezone(timedelta()),
        **kwargs,
    ) -> QuerySet:
        logger.debug(
            "Retrieving object of type %s from datalake.",
            resource_type,
            tags=LogTags.DATALAKE,
        )

        kwargs["get_func"] = "_raw_get"
        kwargs["count_func"] = "None"
        kwargs["collection"] = resource_type.Meta.collection_name
        kwargs["resource_type"] = resource_type
        return QuerySet(
            self,
            limit_,
            skip_,
            sort,
            group_id,
            group_fields,
            tzinfo,
            **kwargs,
        )

    def get_output(self, query: Query) -> List[Dict]:
        raise NotImplementedError()

    def get_dataframe(
        self, resource_type: Type, freq: str = "H", **kwargs
    ) -> pd.DataFrame:
        """Reads documents and returns a dataframe"""
        logger.debug(
            "Retrieving dataframe from datalake.", tags=LogTags.DATALAKE
        )
        documents = self._raw_get(resource_type, **kwargs)
        df = pd.DataFrame([x.dict() for x in documents])
        if not df.empty:
            df.set_index("timestamp", inplace=True, verify_integrity=False)
        return df

    def get_dataset(self, queries: List[Query]) -> pd.DataFrame:
        raise NotImplementedError()

    def save(self, instances: List[DatalakeModel]) -> List[DatalakeModel]:
        documents = [instance.json() for instance in instances]
        if not instances:
            return instances

        logger.debug("Saving instances %s.", instances, tags=LogTags.DATALAKE)

        collection = instances[0].Meta.collection_name

        file_path = os.path.join(
            self._base_path, self._get_file_name(collection)
        )
        handler = FixedLineNumberFileHandler(
            file_path=file_path, total_lines=self._TOTAL_DOCS
        )
        handler.write(documents)
        return instances

    def save_dataframe(
        self, resource_type: DLResource, dataframe: pd.DataFrame
    ) -> None:
        logger.debug("Saving dataframe.", tags=LogTags.DATALAKE)

        instances = dataframe.apply(
            lambda x: resource_type.parse_obj(x.to_dict()), axis=1
        )
        instances = instances.to_list()
        _ = self.save(instances)

    def delete(self, resource_type: DLResource, **kwargs) -> None:
        logger.debug(
            "Deleting resources of type %s from datalake.",
            resource_type,
            tags=LogTags.DATALAKE,
        )
        collection = resource_type.Meta.collection_name
        file_path = os.path.join(
            self._base_path, self._get_file_name(collection)
        )
        handler = FixedLineNumberFileHandler(
            file_path=file_path, total_lines=self._TOTAL_DOCS
        )
        documents = [json.loads(doc) for doc in handler.read()]
        id = kwargs.get("instance_id")
        if id:
            documents = [d for d in documents if d["instance_id"] != id]
        # jsonify python dicts
        documents = [json.loads(json.dumps(d)) for d in documents]
        handler.write(documents, override=True)

    def create_index(self, collection: str, index: list) -> None:
        logger.debug(
            "Skipping index creation when using Local datalake client."
        )

    def raw_aggregate(
        self, collection: str, pipeline: List[Dict]
    ) -> List[Dict]:
        logger.debug(
            "Skipping raw aggregation when using Local datalake client."
        )

    def _filter(
        self, instances: List[DLResource], filters: Dict
    ) -> List[DLResource]:
        filtered = instances
        for key, value in filters.items():
            filtered = filter(partial(value_filter, key, value), filtered)
            filtered = list(filtered)
        return filtered

    def _get_file_name(self, collection: str) -> str:
        return f"{self._PREFIX}{collection}"
