from splight_datalake import MongoClient
from fake_splight_lib.datalake import FakeDatalakeClient
import os

SELECTOR = {
    'fake': FakeDatalakeClient,
    'mongo': MongoClient,
}

DatalakeClient = SELECTOR.get(os.environ.get('DATALAKE', 'fake'))
