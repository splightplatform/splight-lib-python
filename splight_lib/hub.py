from splight_hub import SplightHubClient
from fake_splight_lib.hub import FakeHubClient
import ast
import os


SELECTOR = {
    'fake': FakeHubClient,
    'splight': SplightHubClient,
}


HubClient = SELECTOR.get(os.environ.get('HUB', 'fake'))
