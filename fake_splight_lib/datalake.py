from typing import Dict, List
from datetime import datetime
from splight_lib.communication import Variable
from typing import Dict, List, Type, Optional
from pydantic import BaseModel

class FakeDatalakeClient:
    def __init__(self, database: str = 'default') -> None:
        pass

    def find(self, collection: str, filters: Dict = None, **kwargs) -> List[Dict]:
        return [
            {
                "_id": "jashdasd",
                "asset_id": "1",
                "attribute_id": "1",
                "args": {
                    "value": 1
                },
                "timestamp": datetime.now()
            },
            {
                "_id": "jashdasd",
                "asset_id": "1",
                "attribute_id": "1",
                "args": {
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

    def get(self, resource_type: Type, instances: List[BaseModel], fields: List[str] ,limit: Optional[int] = 1, from_: Optional[datetime] = None, to_: Optional[datetime] = None) -> List[BaseModel]:
        var = self.find("", {})
        vars = []
        for v in instances:
            if v.attribute_id in var:
                v.args = var["args"]
                vars.append(v)
        return vars

    def save(self, resource_type: Type, instances: List[BaseModel]) -> List[BaseModel]:
        pass
