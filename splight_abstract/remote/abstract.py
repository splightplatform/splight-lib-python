from typing import Type, List
from splight_abstract.client import AbstractClient


class AbstractRemoteClient(AbstractClient):
    def _parse_params(self, **kwargs):
        params = {}
        for key, value in kwargs.items():
            params[key] = value
            if isinstance(value, list):
                params[key] = ','.join(value)
        return params
