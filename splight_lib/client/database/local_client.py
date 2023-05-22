import json
import os
from functools import partial
from tempfile import NamedTemporaryFile
from typing import Dict, List, Union
from uuid import uuid4

from splight_lib.client.database.abstract import AbstractDatabaseClient
from splight_lib.client.exceptions import InstanceNotFound
from splight_lib.client.filter import value_filter_on_tuple
from splight_lib.logging._internal import LogTags, get_splight_logger

logger = get_splight_logger()


class LocalDatabaseClient(AbstractDatabaseClient):
    """Database Client implementation for a local database that uses a
    JSON file.
    """

    def __init__(self, path: str, *args, **kwargs):
        super().__init__()
        self._db_file = os.path.join(path, "splight-db.json")

        if not os.path.exists(self._db_file):
            self._save_db(self._db_file, {})
        logger.debug(
            "Local database client initialized.", tags=LogTags.DATABASE
        )

    def save(self, resource_name: str, instance: Dict) -> Dict:
        """Creates or updates a resource depending on the name if
        it contains the id or not.

        Parameters
        ----------
        resource_name: str
            The name of the resource to be created or updated.
        instance : Dict
            A dictionary with resource to be created or updated

        Returns
        -------
        Dict with the created or updated resource.

        Raises
        ------
        InvalidModelName thrown when the model name is not correct.
        """
        logger.debug("Saving instance", tags=LogTags.DATABASE)

        model_name = resource_name.lower()
        if instance.get("id"):
            saved_instance = self._update(model_name, instance)
        else:
            saved_instance = self._create(model_name, instance)
        return saved_instance

    def delete(self, resource_name: str, id: str):
        """Deletes a resource from the database

        Parameters
        ----------
        resource_name : str
            The resource name
        id : str
            The resource's id.

        Raises
        ------
        InvalidModelName thrown when the model name is not correct.
        """
        logger.debug("Deleting instance %s.", id, tags=LogTags.DATABASE)
        model_name = resource_name.lower()
        db = self._load_db_file(self._db_file)
        db_instances = db.get(model_name, {})

        if id not in db_instances:
            raise InstanceNotFound(model_name, id)

        _ = db_instances.pop(id)
        self._save_db(self._db_file, db)

    def operate(self, resource_name: str, instance: Dict) -> Dict:
        raise NotImplementedError("Method not allowed for Local Database")

    def _get(
        self,
        resource_name: str,
        first: bool = False,
        **kwargs,
    ) -> Union[Dict, List[Dict]]:
        """Retrieves one or multiple resources. If the parameter id is passed
        as a kwarg, the instance with that id will be retrieved.

        Parameters
        ----------
        resource_name : str
            The name of the resource.
        first: bool
            Whether to retrieve first element or not.

        Returns
        -------
        Union[Dict, List[Dict]] list of resource or single resource.
        """
        resource_id = kwargs.pop("id", None)
        model_name = resource_name.lower()
        if resource_id:
            result = self._retrieve_single(model_name, resource_id)
        else:
            result = self._retrieve_multiple(model_name, first=first, **kwargs)
        return result

    def _retrieve_single(self, model_name: str, resource_id: str) -> Dict:
        db = self._load_db_file(self._db_file)
        db_instances = db.get(model_name, {})
        if resource_id not in db_instances:
            raise InstanceNotFound(model_name, resource_id)
        return db_instances.get(resource_id)

    def _retrieve_multiple(
        self, model_name: str, first: bool = False, **kwargs
    ) -> List[Dict]:
        db = self._load_db_file(self._db_file)
        db_instances = db.get(model_name, {})

        filters = self._validate_filters(kwargs)
        filtered = self._filter(db_instances, filters=filters)
        instances = list(filtered.values())
        if first:
            return [instances[0]]
        return instances

    def download(
        self, instances: Dict, decrtypt: bool = True, **kwargs
    ) -> NamedTemporaryFile:
        raise NotImplementedError("Method not implemented for Local Database")

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
