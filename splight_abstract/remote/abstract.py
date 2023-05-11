from typing import List, Type

from splight_abstract.client import AbstractClient


class AbstractRemoteClient(AbstractClient):
    def _parse_params(self, **kwargs):
        params = {}
        for key, value in kwargs.items():
            if value is None:
                continue
            params[key] = value
            if isinstance(value, list):
                params[key] = ",".join(value)
        return params
