from typing import List, Dict
from django.utils import timezone


def get_fetch_assets_pipeline(asset_ids: List[int]) -> List[Dict]:

    min_date = timezone.datetime.now() - timezone.timedelta(minutes=10)

    pipe = [
        {'$match':
            {
                'asset_id': {'$in': asset_ids },
                'timestamp': {'$gte': min_date }
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
