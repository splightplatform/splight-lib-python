from uplink.auth import ApiTokenHeader

from .abstract import SplightAPIClientAbstract
from .api import AlgorithmEndpoint


class SplightAPIClient(SplightAPIClientAbstract):
    """Splight API HTTP Clientself.

    Attributes
    ----------
    algorithm
    asset
    attribute
    blockchain
    connector
    datalake
    deployment
    hub
    mapping
    network
    rule
    storage
    common_storage
    tag
    """

    def __init__(self, base_url: str, auth_token: ApiTokenHeader):
        self._algorithm = AlgorithmEndpoint(base_url=base_url, auth=auth_token)

    @property
    def algorithm(self):
        return self._algorithm

    @property
    def asset(self):
        pass

    @property
    def attribute(self):
        pass

    @property
    def blockchain(self):
        pass

    @property
    def connector(self):
        pass

    @property
    def datalake(self):
        pass

    @property
    def deployment(self):
        pass

    @property
    def hub(self):
        pass

    @property
    def mapping(self):
        pass

    @property
    def network(self):
        pass

    @property
    def rule(self):
        pass

    @property
    def storage(self):
        pass

    @property
    def common_storage(self):
        pass

    @property
    def tag(self):
        pass
