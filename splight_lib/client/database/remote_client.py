# import json
from tempfile import NamedTemporaryFile
from typing import Any, Dict, Generator, List, Optional, TypedDict, Union

from furl import furl
from retry import retry

from splight_abstract.database import AbstractDatabaseClient
from splight_abstract.remote import AbstractRemoteClient
from splight_lib.auth import SplightAuthToken
from splight_lib.client.database.classmap import MODEL_NAME_MAP
from splight_lib.client.exceptions import (
    SPLIGHT_REQUEST_EXCEPTIONS,
    InstanceNotFound,
    InvalidModel,
)
from splight_lib.encryption import EncryptionClient
from splight_lib.logging._internal import LogTags, get_splight_logger
from splight_lib.restclient import SplightRestClient
from splight_models import File

logger = get_splight_logger()


class PaginatedResponse(TypedDict):
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: List[Any]


class RemoteDatabaseClient(AbstractDatabaseClient, AbstractRemoteClient):
    """Splight API Database Client.
    Responsible for interacting with database resources using HTTP requests
    to the Splight API.
    """

    def __init__(
        self,
        base_url: str,
        access_id: str,
        secret_key: str,
        *args,
        **kwargs,
    ):
        super().__init__(namespace="default")
        self._base_url = furl(base_url)
        token = SplightAuthToken(
            access_key=access_id,
            secret_key=secret_key,
        )
        self._restclient = SplightRestClient()
        self._restclient.update_headers(token.header)
        logger.debug(
            "Remote database client initialized.", tags=LogTags.DATABASE
        )

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=1)
    def save(self, resource_name: str, instance: Dict):
        """Creates or updates a new resource depending on the model if
        it contains the id or not.

        Parameters
        ----------
        instance : BaseModel
            The instance of the model to be created or updated

        Returns
        -------
        BaseModel with the created or updated resource.

        Raises
        ------
        InvalidModel thrown when the model name is not correct.
        """
        logger.debug("Saving instance", tags=LogTags.DATABASE)

        if instance.get("id"):
            output = self._update(resource_name, instance["id"], instance)
        else:
            output = self._create(resource_name, instance)
        return output

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=1)
    def delete(self, resource_name: str, id: str):
        """Deletes a resource from the database

        Parameters
        ----------
        resource_type : Type
            The resource type to be deleted
        resource_id : str
            The resource's id.

        Raises
        ------
        InvalidModel thrown when the model name is not correct.
        """
        logger.debug("Deleting instance %s.", id, tags=LogTags.DATABASE)
        api_path = self._get_api_path(resource_name)
        url = self._base_url / api_path / f"{id}/"
        response = self._restclient.delete(url)
        response.raise_for_status()

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=1)
    def _get(
        self,
        resource_name: str,
        first: bool = False,
        **kwargs,
    ) -> Union[Dict, List[Dict]]:
        if "id" in kwargs:
            instances = self._retrieve_single(resource_name, id=kwargs["id"])
        else:
            instances = self._retrieve_multiple(
                resource_name, first=first, **kwargs
            )
        return instances

    def _retrieve_multiple(
        self, resource_name: str, first: bool = False, **kwargs
    ) -> List[Dict]:
        api_path = self._get_api_path(resource_name)
        url = self._base_url / api_path
        instances = []
        for page in self._pages(url, page=1, **kwargs):
            instances.extend(page["results"])

        if first:
            return [instances[0]] if instances else []
        return instances

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=1)
    def _retrieve_single(self, resource_name: str, id: str) -> Dict:
        api_path = self._get_api_path(resource_name)
        url = self._base_url / api_path / f"{id}/"
        response = self._restclient.get(url)
        if response.status_code == 404:
            raise InstanceNotFound(resource_name, id)
        else:
            response.raise_for_status()
        return response.json()

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=1)
    def download(
        self,
        resource_name: str,
        instance: Dict,
        decrypt: bool = True,
        **kwargs,
    ) -> NamedTemporaryFile:
        """Returns the number of resources in the database for a given model

        Parameters
        ----------
        instance : BaseModel
            The instance of the model to be downloaded

        Returns
        -------
        TemporaryFile
            the file object

        Raises
        ------
        InvalidModel thrown when the model name is not correct.
        """
        api_path = self._get_api_path(resource_name)
        resource_id = instance.get("id")
        url = self._base_url / api_path / f"{resource_id}/download/"
        response = self._restclient.get(url)
        response.raise_for_status()
        f = NamedTemporaryFile("wb+")
        f.write(response.content)
        f.seek(0)
        if decrypt and instance.encrypted:
            encryption_manager = EncryptionClient()
            encryption_manager.decrypt_file(path=f.name)
        logger.debug("Downloaded instance %s.", id, tags=LogTags.DATABASE)
        return f

    def _pages(
        self, url: furl, **kwargs
    ) -> Generator[PaginatedResponse, None, None]:
        next_page = kwargs["page"]
        while next_page:
            response = self._list(url, **kwargs)
            yield response
            next_page = (
                response["next"].split("page=")[1]
                if response["next"]
                else None
            )
            kwargs["page"] = next_page

    def _list(self, url: furl, **kwargs) -> PaginatedResponse:
        params = self._parse_params(**kwargs)
        response = self._restclient.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def _create(self, resource_name: str, instance: Dict) -> Dict:
        model_name = resource_name.lower()
        api_path = self._get_api_path(resource_name)
        url = self._base_url / api_path
        if model_name == "file":
            with open(instance["file"], "rb") as f:
                file = {"file": f}
                response = self._restclient.post(
                    url, data=instance, files=file
                )
        else:
            response = self._restclient.post(url, data=instance)

        response.raise_for_status()
        return response.json()

    def _update(
        self, resource_name: str, resource_id: str, instance: Dict
    ) -> Dict:
        api_path = self._get_api_path(resource_name)
        url = self._base_url / api_path / f"{resource_id}/"
        response = self._restclient.put(url, data=instance)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _get_api_path(resource_name: str) -> str:
        api_path = MODEL_NAME_MAP.get(resource_name.lower())
        if not api_path:
            raise InvalidModel(resource_name.lower())
        return api_path
