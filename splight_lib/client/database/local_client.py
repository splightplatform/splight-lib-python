import json
import os
from functools import partial
from tempfile import NamedTemporaryFile
from typing import Dict, List, Union
from uuid import uuid4

from splight_abstract.database import AbstractDatabaseClient
from splight_lib.client.exceptions import InstanceNotFound
from splight_lib.client.filter import value_filter_on_tuple
from splight_lib.logging._internal import LogTags, get_splight_logger

# from splight_lib.models.base import SplightBaseModel

# from splight_models import SplightBaseModel

# ResourceType = Type[SplightBaseModel]

logger = get_splight_logger()


class LocalDatabaseClient(AbstractDatabaseClient):
    """Database Client implementation for a local database that uses a
    JSON file.
    """

    def __init__(self, path: str, *args, **kwargs):
        super().__init__(namespace="default")
        self._db_file = os.path.join(path, "splight-db.json")

        if not os.path.exists(self._db_file):
            self._save_db(self._db_file, {})
        logger.debug(
            "Local database client initialized.", tags=LogTags.DATABASE
        )

    def save(self, resource_name: str, instance: Dict) -> Dict:
        """Saves an instance in the local database, if the instance has an id
        will try to update the instance, otherwise it will create a new one.

        Parameters
        ----------
        instance : SplightBaseModel
            The instance to be saved in the database.
        """
        logger.debug("Saving instance", tags=LogTags.DATABASE)

        model_name = resource_name.lower()
        if instance.get("id"):
            saved_instance = self._update(model_name, instance)
        else:
            saved_instance = self._create(model_name, instance)
        return saved_instance

    def delete(self, resource_name: str, id: str):
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
        model_name = resource_name.lower()
        db = self._load_db_file(self._db_file)
        db_instances = db.get(model_name, {})

        if id not in db_instances:
            raise InstanceNotFound(model_name, id)

        _ = db_instances.pop(id)
        self._save_db(self._db_file, db)

    def _get(
        self,
        resource_name: str,
        first: bool = False,
        **kwargs,
    ) -> Union[Dict, List[Dict]]:
        """Reads one or multiple objects in the database."""
        db = self._load_db_file(self._db_file)
        model_name = resource_name.lower()
        db_instances = db.get(model_name, {})

        resource_id = kwargs.pop("id", None)
        raw_instances = db_instances
        if resource_id:
            if resource_id not in db_instances:
                raise InstanceNotFound(model_name, resource_id)
            raw_instances = {resource_id: db_instances.get(resource_id, {})}

        filters = self._validate_filters(kwargs)
        filtered = self._filter(raw_instances, filters=filters)
        instances = list(filtered.values())
        if first:
            return [instances[0]]
        return instances

    def download(
        self, instances: Dict, decrtypt: bool = True, **kwargs
    ) -> NamedTemporaryFile:
        raise NotImplementedError()

    def _create(self, resource_name: str, instance: Dict) -> Dict:
        db = self._load_db_file(self._db_file)
        db_instances = db.get(resource_name, {})
        instance["id"] = str(uuid4())
        db_instances.update({instance["id"]: instance})
        db[resource_name] = db_instances
        self._save_db(self._db_file, db)
        return instance

    def _update(self, resource_name: str, instance: Dict) -> Dict:
        db = self._load_db_file(self._db_file)
        db_instances = db.get(resource_name, {})

        if instance["id"] not in db_instances:
            raise InstanceNotFound(resource_name, instance["id"])
        db_instances[instance["id"]] = instance
        self._save_db(self._db_file, db)
        return instance

    def _filter(
        self, instances: Dict[str, Dict], filters: Dict
    ) -> Dict[str, Dict]:
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
