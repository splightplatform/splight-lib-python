from splight_datalake import DatalakeClient, FileManager
from fake_splight_lib.datalake import FakeDatalakeClient
import ast
import os

if ast.literal_eval(os.getenv("FAKE_DATALAKE", "True")):
    DatalakeClient = FakeDatalakeClient
