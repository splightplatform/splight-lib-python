import json
import os
from datetime import datetime, timedelta, timezone
from functools import partial
from typing import Dict, List, Optional, Union

import pandas as pd

from splight_lib.client.datalake.abstract import AbstractDatalakeClient
from splight_lib.client.file_handler import FixedLineNumberFileHandler
from splight_lib.client.filter import value_filter
from splight_lib.logging._internal import LogTags, get_splight_logger

logger = get_splight_logger()


class LocalDatalakeClient(AbstractDatalakeClient):
    """Datalake client implementation for a storing locally documents
    in different files.
    """

    _DEFAULT = "default"
    _PREFIX = "splight-dl_"
    _SUFFIX = ".json"
    _TOTAL_DOCS = 10000

    def __init__(self, path: str, *args, **kwargs):
        super().__init__()
        self._base_path = path
        logger.info(
            "Local datalake client initialized.", tags=LogTags.DATALAKE
        )

    def save(
        self,
        collection: str,
        instances: Union[List[Dict], Dict],
    ) -> List[Dict]:
        instances = instances if isinstance(instances, list) else [instances]

        logger.debug("Saving instances %s.", instances, tags=LogTags.DATALAKE)
        instances = [json.dumps(instance) for instance in instances]

        file_path = os.path.join(
            self._base_path, self._get_file_name(collection)
        )
        handler = FixedLineNumberFileHandler(
            file_path=file_path, total_lines=self._TOTAL_DOCS
        )
        handler.write(instances)
        return instances

    def _raw_get(
        self,
        resource_name: str,
        collection: str,
        limit_: int = 1000,
        skip_: int = 0,
        sort: Union[List, str] = ["timestamp__desc"],
        group_id: Optional[Union[List, str]] = None,
        group_fields: Optional[Union[List, str]] = None,
        tzinfo: timezone = timezone(timedelta()),
        **filters,
    ) -> List[Dict]:
        filters.update(
            {
                "output_format": resource_name,
            }
        )
        filters = self._parse_filters(filters)

        file_path = os.path.join(
            self._base_path, self._get_file_name(collection)
        )
        handler = FixedLineNumberFileHandler(
            file_path=file_path, total_lines=self._TOTAL_DOCS
        )
        documents = [
            json.loads(doc) for doc in handler.read()[skip_ : skip_ + limit_]
        ]
        documents = self._filter(documents, filters=filters)

        reverse = False
        if "__desc" not in sort:
            reverse = True
        documents.sort(key=lambda x: x["timestamp"], reverse=reverse)

        return documents

    def get_dataframe(
        self,
        resource_name: str,
        collection: str,
        sort: Union[List, str] = ["timestamp__desc"],
        group_id: Optional[Union[List, str]] = None,
        group_fields: Optional[Union[List, str]] = None,
        tzinfo: timezone = timezone(timedelta()),
        **filters,
    ) -> pd.DataFrame:
        logger.debug(
            "Retrieving dataframe from datalake.", tags=LogTags.DATALAKE
        )

        filters.update(
            {
                "resource_name": resource_name,
                "collection": collection,
                "sort": sort,
                "group_id": group_id,
                "group_fields": group_fields,
                "tzinfo": tzinfo,
            }
        )

        documents = self._raw_get(**filters)
        df = pd.DataFrame(documents)

        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df.set_index("timestamp", inplace=True, verify_integrity=False)

        return df

    def save_dataframe(self, collection: str, dataframe: pd.DataFrame) -> None:
        logger.debug("Saving dataframe.", tags=LogTags.DATALAKE)

        dataframe["timestamp"] = dataframe["timestamp"].astype(str)
        instances = list(dataframe.to_dict("index").values())
        _ = self.save(collection, instances)

    def delete(self, collection: str, **kwargs) -> None:
        logger.debug(
            "Skipping deleting objects when using Local datalake client."
        )

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

    def execute_query(
        self,
        from_timestamp: datetime,
        to_timestamp: Optional[datetime],
        query: Dict,
    ) -> pd.DataFrame:
        raise NotImplementedError("Method not available for the local client")

    def _filter(self, instances: List[dict], filters: Dict) -> List[dict]:
        filtered = instances
        for key, value in filters.items():
            filtered = filter(partial(value_filter, key, value), filtered)
            filtered = list(filtered)
        return filtered

    def _parse_filters(self, filters: List[dict]):
        new_filters = {}
        for key, value in filters.items():
            if value is None:
                continue
            new_filters[key] = value
        return new_filters

    def _get_file_name(self, collection: str) -> str:
        return f"{self._PREFIX}{collection}{self._SUFFIX}"
