from typing import Dict, List
from datetime import datetime
from splight_lib.communication import Variable


class FakeDatalakeClient:
    def __init__(self, database: str = 'default') -> None:
        pass

    def find(self, collection: str, filters: Dict = None, **kwargs) -> List[Dict]:
        return [
            {
                "_id": "jashdasd",
                "asset_id": "1",
                "p": {
                    "value": 1
                },
                "timestamp": datetime.now()
            },
            {
                "_id": "jashdasd",
                "asset_id": "1",
                "p": {
                    "value": 4
                },
                "timestamp": datetime.now()
            }
        ]

    def delete_many(self, collection: str, filters: Dict = {}) -> None:
        pass

    def insert_many(self, collection: str, data: List[Dict], **kwargs) -> None:
        pass

    def aggregate(self, collection: str, pipeline: List[Dict]) -> List[Dict]:
        return {
            "_id": "jashdasd",
            "asset_id": "1",
            "p": {
                "value": 5
            },
            "timestamp": datetime.now()
        }

    def fetch_updates(self, variables: List[Variable]) -> List[Variable]:
        var = self.aggregate("", [])
        vars = []
        for v in variables:
            if v.attribute_id in var:
                v.args = var[v.attribute_id]
                vars.append(v)
        return vars

    def push_updates(self, variables: List[Variable]) -> None:
        pass
