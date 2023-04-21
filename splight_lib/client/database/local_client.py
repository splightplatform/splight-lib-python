import json
import os
from functools import partial
from tempfile import NamedTemporaryFile
from typing import Dict, List, Type, Union
from uuid import uuid4

from splight_abstract.database import AbstractDatabaseClient
from splight_lib.client.exceptions import InstanceNotFound
from splight_lib.client.filter import value_filter_on_tuple
from splight_lib.logging._internal import LogTags, get_splight_logger
from splight_models import SplightBaseModel

ResourceType = Type[SplightBaseModel]

logger = get_splight_logger()


class LocalDatabaseClient(AbstractDatabaseClient):
    """Database Client implementation for a local database that uses a
    JSON file.
    """

    def __init__(self, namespace: str, path: str, *args, **kwargs):
        super().__init__(namespace)
        self._db_file = os.path.join(path, "splight-db.json")

        if not os.path.exists(self._db_file):
            self._save_db(self._db_file, {})
        logger.info(
            "Local database client initialized.", tags=LogTags.DATABASE
        )

    def save(self, instance: SplightBaseModel) -> SplightBaseModel:
        """Saves an instance in the local database, if the instance has an id
        will try to update the instance, otherwise it will create a new one.

        Parameters
        ----------
        instance : SplightBaseModel
            The instance to be saved in the database.

        Returns
        -------
        SplightBaseModel: The instances saved in the database.
        """
        logger.debug("Saving instance %s.", instance.id, tags=LogTags.DATABASE)

        model_class = type(instance)
        model_name = model_class.__name__.lower()
        if instance.id:
            new_instance = self._update(model_name, instance)
        else:
            new_instance = self._create(model_name, instance)
        return new_instance

    def delete(self, resource_type: ResourceType, id: str):
        """Deletes an object in the database based on the type and the id.

        Parameters
        ----------
        resource_type: ResourceType
            The type of the object to be deleted.
        id: str
            The object's id to delete.

        Raises
        ------
        InstanceNotFound if the object with the given id is not in the database
        """
        logger.debug("Deleting instance %s.", id, tags=LogTags.DATABASE)
        model_name = resource_type.__name__.lower()
        db = self._load_db_file(self._db_file)
        db_instances = db.get(model_name, {})

        if id not in db_instances:
            raise InstanceNotFound(model_name, id)

        _ = db_instances.pop(id)
        self._save_db(self._db_file, db)

    def _get(
        self,
        resource_type: ResourceType,
        first: bool = False,
        limit_: int = -1,
        skip_: int = 0,
        page_size: int = -1,
        deleted: bool = False,
        **kwargs,
    ) -> Union[SplightBaseModel, List[SplightBaseModel]]:
        """Reads one or multiple objects in the database."""
        db = self._load_db_file(self._db_file)
        model_name = resource_type.__name__.lower()
        db_instances = db.get(model_name, {})

        resource_id = kwargs.pop("id", None)
        instances = db_instances
        if resource_id:
            instances = {resource_id: db_instances.get(resource_id, {})}

        filters = self._validate_filters(kwargs)
        filtered = self._filter(instances, filters=filters)
        parsed = [resource_type.parse_obj(item) for item in filtered.values()]
        if first:
            return parsed[0] if parsed else None
        return parsed

    def count(self, resource_type: ResourceType, **kwargs) -> int:
        db = self._load_db_file(self._db_file)
        model_name = resource_type.__name__.lower()
        db_instances = db.get(model_name, {})
        logger.debug(
            "Counted %s objects of type: %s.",
            response["count"],
            resource_type,
            tags=LogTags.DATABASE,
        )
        return len(db_instances)

    def download(
        self, instances: SplightBaseModel, decrtypt: bool = True, **kwargs
    ) -> NamedTemporaryFile:
        raise NotImplementedError()

    def _create(
        self, model_name: str, instance: SplightBaseModel
    ) -> SplightBaseModel:
        db = self._load_db_file(self._db_file)
        db_instances = db.get(model_name, {})
        instance.id = str(uuid4())
        db_instances.update({instance.id: instance.dict()})
        db[model_name] = db_instances
        self._save_db(self._db_file, db)
        return instance

    def _update(
        self, model_name: str, instance: SplightBaseModel
    ) -> SplightBaseModel:
        db = self._load_db_file(self._db_file)
        db_instances = db.get(model_name, {})

        if instance.id not in db_instances:
            raise InstanceNotFound(model_name, instance.id)
        db_instances[instance.id] = instance.dict()
        self._save_db(self._db_file, db)
        return instance

    def _filter(
        self, instances: Dict[str, SplightBaseModel], filters: Dict
    ) -> Dict[str, SplightBaseModel]:
        filtered = instances
        for key, value in filters.items():
            filtered = filter(
                partial(value_filter_on_tuple, key, value), filtered.items()
            )
            filtered = {item[0]: item[1] for item in filtered}
        return filtered

    def _load_db_file(self, file_path: str) -> Dict:
        with open(file_path, "r") as fid:
            data = json.load(fid)
        return data

    def _save_db(self, file_path: str, db: Dict):
        with open(file_path, "w") as fid:
            json.dump(db, fid, indent=2)

    def _validate_filters(self, filters_raw: Dict):
        invalid_filters = ["ignore_hook"]
        return {
            key: value
            for key, value in filters_raw.items()
            if key not in invalid_filters
        }
