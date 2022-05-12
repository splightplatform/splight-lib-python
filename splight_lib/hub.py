from splight_hub import SplightHubClient
from fake_splight_lib.hub import FakeHubClient
import ast
import os

HubClient = SplightHubClient

if ast.literal_eval(os.getenv("FAKE_HUB", "True")):
    HubClient = FakeHubClient
