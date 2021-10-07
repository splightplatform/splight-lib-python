from splight_lib.component import ComponentType, DOComponentInterface
from splight_lib.asset import Network


class FakeComponent(DOComponentInterface):
    type = ComponentType.UNKNOWN

    def execute(self, network: Network):
        pass
