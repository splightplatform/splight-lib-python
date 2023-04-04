import os
from datetime import timedelta, timezone
from typing import Dict, List, Type, Union

import pandas as pd

from splight_abstract.client import QuerySet
from splight_abstract.datalake import AbstractDatalakeClient
from splight_models import DatalakeModel, Query

DLResource = Type[DatalakeModel]


class LocalDatalakeClient(AbstractDatalakeClient):

    _DEFAULT = "default"
    _PREFIX = "dl_"

    def __init__(self, namespace: str, path: str):
        super().__init__(namespace=namespace)
        self._base_path = path

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
        pass

    def get_output(self, query: Query) -> List[Dict]:
        pass

    def get_dataframe(
        self, resource_type: Type, freq="H", **kwargs
    ) -> pd.DataFrame:
        pass

    def get_dataset(self, queries: List[Query]) -> pd.DataFrame:
        pass

    def save(self, instances: List[DatalakeModel]) -> List[DatalakeModel]:
        documents = [f"{instance.json()}\n" for instance in instances]
        collection = instances[0].Meta.collection_name

        file_path = os.path.join(
            self._base_path, self._get_file_name(collection)
        )
        with open(file_path, "a") as fid:
            fid.writelines(documents)
        return instances

    def save_dataframe(
        self, resource_type: DLResource, dataframe: pd.DataFrame
    ) -> None:

        instances = dataframe.apply(
            lambda x: resource_type.parse_obj(x.to_dict()), axis=1
        )
        instances = instances.to_list()
        _ = self.save(instances)

    def delete(self, resource_type: DLResource, **kwargs) -> None:
        pass

    def create_index(self, collection: str, index: list) -> None:
        raise NotImplementedError()

    def raw_aggregate(
        self, collection: str, pipeline: List[Dict]
    ) -> List[Dict]:
        pass

    def _get_file_name(self, collection: str) -> str:
        return f"{self._PREFIX}{collection}"
