from splight_datalake import MongoClient, S3Manager
from splight_datalake import MongoPipelines
from fake_splight_lib.datalake import FakeDatalakeClient
import ast
import os
import sys

DatalakeClient = MongoClient
TESTING = "test" in sys.argv

if TESTING or ast.literal_eval(os.getenv("FAKE_DATALAKE", "True")):
    DatalakeClient = FakeDatalakeClient
