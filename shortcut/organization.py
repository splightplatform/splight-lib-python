from splight_lib.communication import ExternalCommunicationClient
from splight_lib.database import DatabaseClient
from splight_lib.deployment import DeploymentClient
from splight_models.namespace import Namespace


class OrganizationHandler:

    @staticmethod
    def create(id: str):
        id = str(id)
        # TODO add Auth0 step
        ExternalCommunicationClient.create_topic(id)
        namespace = Namespace(id=id)
        # TODO add step ExternalCommunicationClient.save(namespace)
        DeploymentClient().save(instance=namespace)
        return DatabaseClient().save(namespace)
    
    @staticmethod
    def delete(id):
        # TODO add step ExternalCommunicationClient.save(namespace)
        DeploymentClient().delete(Namespace, id=id)
        return DatabaseClient().delete(Namespace, id=id) # TODO logic delete
