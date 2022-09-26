from typing import Type, List
from splight_abstract.client import AbstractClient


class AbstractRemoteClient(AbstractClient):
    list_type_trailings = ("__in", )

    def _parse_params(self, **kwargs):
        params = {}
        for key, value in kwargs.items():
            if key.endswith(self.list_type_trailings):
                params[key] = ','.join(value)
            else:
                params[key] = value
        return params
