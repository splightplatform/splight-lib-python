from .utils import Pipeline
from typing import List
from django.utils import timezone


def get_fetch_assets_pipeline(asset_ids: List[int], max_backward_time=10) -> Pipeline:

    min_date = timezone.now() - timezone.timedelta(minutes=max_backward_time)

    pipe = [
        {'$match':
            {
                'asset_id': {'$in': asset_ids},
                'timestamp': {'$gte': min_date}
            }
         },
        {"$sort":
            {
                "timestamp": 1
            }
         },
        {'$group':
            {
                '_id': {'asset_id': '$asset_id'},
                'item': {'$mergeObjects': '$$ROOT'},
            }
         },
        {'$replaceRoot':
            {
                'newRoot': '$item'
            }
         },
        {"$project":
            {
                "_id": 0,
                "timestamp": 0
            }
         }
    ]
    return pipe
