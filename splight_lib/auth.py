import os

from splight_auth.manager import AuthClient
from fake_splight_lib.auth import FakeAuthClient

AUTH_REGISTRY = {
    "fake": FakeAuthClient,
    "splight": AuthClient
}


SplightAuthClient = AUTH_REGISTRY.get(os.getenv("AUTH", "fake"))
