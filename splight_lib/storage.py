import os
import ast
from fake_splight_lib.storage import FakeStorageClient
from splight_storage import S3StorageClient
from splight_models import StorageFile

StorageClient = S3StorageClient

if ast.literal_eval(os.getenv("FAKE_STORAGE", "True")):
    StorageClient = FakeStorageClient

__all__ = [
    "StorageClient",
    "StorageFile",
]
