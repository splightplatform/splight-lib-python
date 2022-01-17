from .mongo import MongoClient

__all__ = [
    MongoClient,
]

DatalakeClient = MongoClient
