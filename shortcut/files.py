import os


from typing import List, Any, Union, Optional
from splight_lib.communication import Variable, Message, Action, ExternalCommunicationClient
from splight_lib.datalake import DatalakeClient
from splight_lib.storage import StorageClient, StorageFile
from splight_models import *
from splight_lib import logging

logger = logging.getLogger()

COLLECTION = 'storage'


def save_file(storage_client: StorageClient, datalake_client: DatalakeClient,
              filename, prefix: Optional[str] = None,
              asset_id: Optional[str] = None, attribute_id: Optional[str] = None, path: str = '', args: Dict = {}) -> None:
    if not os.path.exists(filename):
        logger.error("File must be locally found")
        raise Exception()
    if asset_id and not attribute_id:
        msg = "Given asset but no attribute"
        logger.error(msg)
        raise Exception(msg)
    if attribute_id and not asset_id:
        msg = "Given attribute but no asset"
        logger.error(msg)
        raise Exception(msg)

    var = Variable(asset_id=asset_id, attribute_id=attribute_id, path=path, args=args)
    datalake_client.save(Variable, var, collection=COLLECTION)
    storage_client.save(StorageFile(filename), prefix=prefix)
