from splight_models.namespace import Namespace
from splight_lib import logging
from splight_lib.settings import setup


DatabaseClient = setup.DATABASE_CLIENT
DeploymentClient = setup.DEPLOYMENT_CLIENT
logger = logging.getLogger()


class OrganizationHandler:

    @staticmethod
    def create(id: str):
        id = str(id)
        # TODO add Auth0 step
        namespace = Namespace(id=id)
        DeploymentClient().save(instance=namespace)
        return DatabaseClient().save(namespace)
    
    @staticmethod
    def delete(id):
        DeploymentClient().delete(Namespace, id=id)
        return DatabaseClient().delete(Namespace, id=id) # TODO logic delete
