from splight_models.namespace import Namespace
from splight_lib import logging
from splight_lib.settings import splight_settings


DatabaseClient = splight_settings.DATABASE_CLIENT
DeploymentClient = splight_settings.DEPLOYMENT_CLIENT
logger = logging.getLogger()


class OrganizationHandler:

    @staticmethod
    def create(id: str):
        id = str(id)
        # TODO add Auth0 step
        namespace = Namespace(id=id)
        # TODO add step ExternalCommunicationClient.save(namespace)
        DeploymentClient().save(instance=namespace)
        return DatabaseClient().save(namespace)
    
    @staticmethod
    def delete(id):
        # TODO add step ExternalCommunicationClient.save(namespace)
        DeploymentClient().delete(Namespace, id=id)
        return DatabaseClient().delete(Namespace, id=id) # TODO logic delete
