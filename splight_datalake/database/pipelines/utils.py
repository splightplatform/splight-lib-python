from typing import Dict, List, Optional
from datetime import timedelta
from datetime import datetime


Stage = Dict
Pipeline = List[Dict]


def time_range_filter(from_: Optional[datetime], to_: Optional[datetime]) -> Dict:
    """
        Add this to a match aggregation stage to filter between from, to times.
    """
    match = {
        "timestamp": {}
    }
    if from_:
        match["timestamp"]["$gte"] = from_
    if to_:
        match["timestamp"]["$lte"] = to_

    if match["timestamp"]:
        return match

    return {}


def attributes_filter(attributes: List[str]) -> Dict:
    """
    This function returns a filter for the match stage that will match
    the documents that have any of the attributes in attributes.
    """

    res = {"$or": [{attr: {"$exists": 1}} for attr in attributes]}

    # This is always False, so if attribtues is empty, this filter will exclude all documents
    res["$or"].append({"_id": {"$exists": 0}})

    return res


def asset_filter(asset_id: int) -> Dict:
    return {"asset_id": asset_id}


def get_match_timestamp_intervals_pipeline(time_interval: timedelta) -> Pipeline:
    if time_interval.days > 0:
        raise ValueError("time_interval must be less than a day")

    return [
        # decompose the timestamp into its parts
        {
            "$addFields": {
                "timestamp": {
                    "year": {"$year": "$timestamp"},
                    "month": {"$month": "$timestamp"},
                    "day": {"$dayOfMonth": "$timestamp"},
                    "hours": {"$hour": "$timestamp"},
                    "minutes": {"$minute": "$timestamp"},
                    "seconds": {"$second": "$timestamp"},
                }
            }
        },
        {  # Get the secods of the timestamp day
            "$addFields": {
                "timestamp_secods": {
                    "$add": [
                        "$timestamp.seconds",
                        {"$multiply": ["$timestamp.minutes", 60]},
                        {"$multiply": ["$timestamp.hours", 60 * 60]},
                    ]
                }
            }
        },
        {  # Transform the time
            "$addFields": {
                "timestamp_secods": {
                    "$subtract": [
                        "$timestamp_secods",
                        {"$mod": ["$timestamp_secods", int(time_interval.total_seconds())]}
                    ]
                }
            }
        },
        {  # Re create the time parts
            "$addFields": {
                "timestamp": {
                    "year": {"$toString": "$timestamp.year"},
                    "month": {"$toString": "$timestamp.month"},
                    "day": {"$toString": "$timestamp.day"},
                    "hours": {"$toString": {"$mod": [{"$floor": {"$divide": ["$timestamp_secods", 60 * 60]}}, 24]}},
                    "minutes": {"$toString": {"$mod": [{"$floor": {"$divide": ["$timestamp_secods", 60]}}, 60]}},
                    "seconds": {"$toString": {"$mod": ["$timestamp_secods", 60]}},
                }
            }
        },
        {  # Create the time object
            "$addFields": {
                "timestamp": {
                    "$toDate": {
                        "$concat": ["$timestamp.year",
                                    "-",
                                    "$timestamp.month",
                                    "-",
                                    "$timestamp.day",
                                    " ",
                                    "$timestamp.hours",
                                    ":",
                                    "$timestamp.minutes",
                                    ":",
                                    "$timestamp.seconds"]
                    }
                }
            }
        },
        {  # Removee the timestamp_secods field
            "$project": {
                "timestamp_secods": 0,
            }
        }
    ]
