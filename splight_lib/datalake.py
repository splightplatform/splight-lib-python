from splight_datalake import MongoClient, S3Manager
from fake_splight_lib.datalake import FakeDatalakeClient
import ast
import os


DatalakeClient = MongoClient


if ast.literal_eval(os.getenv("FAKE_DATALAKE", "True")):
    DatalakeClient = FakeDatalakeClient
