import os
from fake_splight_lib.storage import FakeStorageClient
from splight_storage import S3StorageClient
from splight_models import StorageFile

SELECTOR = {
    'fake': FakeStorageClient,
    's3': S3StorageClient,
}

StorageClient = SELECTOR.get(os.environ.get('STORAGE', 'fake'))

__all__ = [
    "StorageClient",
    "StorageFile",
]
