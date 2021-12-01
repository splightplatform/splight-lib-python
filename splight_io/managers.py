from abc import ABCMeta, abstractmethod
from splight_io.communication import AbstractComunication, Data


class IOAction:
    SUBSCRIBE = 'subscribe'
    UNSUBSCRIBE = 'unsubscribe'
    WRITE = 'write'


class IOManager(metaclass=ABCMeta):
    def __init__(self, communication: AbstractComunication):
        self.comm = communication

    def remote_action(self, action, mapping):
        connector = mapping.connector.id
        variable = mapping.external_variable
        action = action.value
        data = Data(action=action, variable=variable, connector=connector)
        self.comm.send(data)

    def write(self, mappings, value):
        data = value
        # TODO build data from value
        for mapping in mappings:
            return self.remote_action(IOAction.WRITE, mapping, data)

    @abstractmethod
    def deploy_component(self):
        pass


class ClientManager(IOManager):
    def read(self):
        raise NotImplementedError

    def deploy_component(self):
        # TODO
        pass


class ServerManager(IOManager):
    def read(self):
        data = self.comm.receive()
        # TODO unbuild data to value
        return data

    def deploy_component(self):
        # TODO
        pass
