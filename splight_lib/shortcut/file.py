import os
from typing import Optional
from splight_models import *
from splight_lib import logging
from splight_lib.settings import setup


COLLECTION = 'files'
DatalakeClient = setup.DATALAKE_CLIENT
StorageClient = setup.STORAGE_CLIENT
logger = logging.getLogger()


def save_file(storage_client: StorageClient, datalake_client: DatalakeClient,
              filename, prefix: Optional[str] = None,
              asset_id: Optional[str] = None, attribute_id: Optional[str] = None, path: str = '', args: Dict = None) -> StorageFile:
    if not os.path.exists(filename):
        logger.error("File must be locally found")
        raise Exception()
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