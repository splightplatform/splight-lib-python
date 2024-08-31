from enum import Enum


class StepName(str, Enum):
    ADD_FIELDS = "addFields"
    ADD_TO_SET = "addToSet"
    BUCKET = "bucket"
    BUCKET_AUTO = "bucketAuto"
    BUCKET_GROUP = "bucketGroup"
    COUNT = "count"
    FACET = "facet"
    GRAPH_LOOKUP = "graphLookup"
    GROUP = "group"
    INDEX_STATS = "indexStats"
    LIMIT = "limit"
    LIST_SESSIONS = "listSessions"
    LOOKUP = "lookup"
    MATCH = "match"
    MERGE = "merge"
    OUT = "out"
    PLAN_CACHE_STATS = "planCacheStats"
    PROJECT = "project"
    REDACT = "redact"
    REPLACE_ROOT = "replaceRoot"
    REPLACE_WITH = "replaceWith"
    SAMPLE = "sample"
    SET = "set"
    SKIP = "skip"
    SORT = "sort"
    UNSET = "unset"
    UNWIND = "unwind"


class TraceType(str, Enum):
    QUERY = "QUERY"
    EXPRESSION = "EXPRESSION"
    METADATA = "METADATA"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)