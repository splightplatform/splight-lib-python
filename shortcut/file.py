from logging import raiseExceptions
import os


from typing import List, Any, Union, Optional
from splight_lib.communication import Variable, Message, Action, ExternalCommunicationClient
from splight_lib.datalake import DatalakeClient
from splight_lib.storage import StorageClient, StorageFile
from splight_models import *
from splight_lib import logging

logger = logging.getLogger()

COLLECTION = 'files'


def save_file(storage_client: StorageClient, datalake_client: DatalakeClient,
              filename, prefix: Optional[str] = None,
              asset_id: Optional[str] = None, attribute_id: Optional[str] = None, path: str = '', args: Dict = None) -> StorageFile:
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
    args = args if args else dict()
    if args.get('file_id',None) is not None:
        msg = "Can't overwrite file_id"
        logger.error(msg)
        raise Exception(msg)
    file = storage_client.save(StorageFile(file=filename,content_type='str'), prefix=prefix)
    args['file_id'] = file.id
    var = Variable(asset_id=asset_id, attribute_id=attribute_id, path=path, args=args)
    datalake_client.save(Variable, instances=[var], collection=COLLECTION)
    return file