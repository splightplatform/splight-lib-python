from tempfile import NamedTemporaryFile
from typing import Any, Dict, Generator, List, Optional, Union

import progressbar
import requests
from furl import furl
from httpx._status_codes import codes
from retry import retry
from typing_extensions import TypedDict

from splight_lib.abstract.client import AbstractRemoteClient
from splight_lib.auth import SplightAuthToken
from splight_lib.client.database.abstract import AbstractDatabaseClient
from splight_lib.client.database.classmap import (
    CUSTOM_PATHS_MAP,
    MODEL_NAME_MAP,
)
from splight_lib.client.exceptions import (
    SPLIGHT_REQUEST_EXCEPTIONS,
    InstanceNotFound,
    InvalidModel,
    InvalidModelName,
    RequestError,
)
from splight_lib.constants import ENGINE_PREFIX
from splight_lib.logging._internal import LogTags, get_splight_logger
from splight_lib.restclient import SplightRestClient

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
        super().__init__()
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
    def save(
        self,
        resource_name: str,
        instance: Dict,
        files: Optional[Dict[str, str]] = None,
    ) -> Dict:
        """Creates or updates a resource depending on the name if
        it contains the id or not.

        Parameters
        ----------
        resource_name: str
            The name of the resource to be created or updated.
        instance : Dict
            A dictionary with resource to be created or updated
        files: Optional[Dict[str, srt]] = None
            A dictionary with the name and the file path to the files to be
            pushed

        Returns
        -------
        Dict with the created or updated resource.

        Raises
        ------
        InvalidModelName thrown when the model name is not correct.
        """
        if instance.get("id"):
            output = self._update(
                resource_name, instance["id"], instance, files
            )
        else:
            output = self._create(resource_name, instance, files)
        return output

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=1)
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
        api_path = self._get_api_path(resource_name)
        url = self._base_url / api_path / f"{id}/"
        response = self._restclient.delete(url)
        if response.is_error:
            raise RequestError(response.status_code, response.text)

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=1)
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
        if kwargs.get("id"):
            instances = self._retrieve_single(resource_name, id=kwargs["id"])
        else:
            instances = self._retrieve_multiple(
                resource_name, first=first, **kwargs
            )
        return instances

    def operate(self, resource_name: str, instance: Dict) -> Dict:
        model_name = resource_name.lower()
        api_path = CUSTOM_PATHS_MAP.get(model_name)
        if not api_path:
            raise InvalidModelName(model_name)
        api_path = api_path.format_map({"prefix": ENGINE_PREFIX, **instance})
        url = self._base_url / api_path
        response = self._restclient.post(url, json=instance)
        if response.is_error:
            raise RequestError(response.status_code, response.text)
        return response.json()

    def _retrieve_multiple(
        self, resource_name: str, first: bool = False, **kwargs
    ) -> List[Dict]:
        logger.debug(f"Retrieving objects {resource_name}")
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
        logger.debug(f"Retrieving object {resource_name} with id {id}")
        api_path = self._get_api_path(resource_name)
        url = self._base_url / api_path / f"{id}/"
        response = self._restclient.get(url)
        if response.status_code == codes.NOT_FOUND:
            raise InstanceNotFound(resource_name, id)
        elif response.is_error:
            raise RequestError(response.status_code, response.text)
        return response.json()

    @retry(SPLIGHT_REQUEST_EXCEPTIONS, tries=3, delay=1)
    def download(
        self,
        resource_name: str,
        instance: Dict,
        type_: Optional[str] = None,
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
        InvalidModelName thrown when the model name is not correct.
        """
        if resource_name.lower() not in ["file", "hubsolutionversion"]:
            raise InvalidModel(
                "Only files and hub solution can be downloaded."
            )
        api_path = self._get_api_path(resource_name)
        resource_id = instance.get("id")
        url = self._base_url / api_path / f"{resource_id}/download_url/"
        params = {"type": type_} if type_ else {}
        response = self._restclient.get(url, params=params)
        if response.is_error:
            raise RequestError(response.status_code, response.text)
        download_url = response.json().get("url")

        file = NamedTemporaryFile(mode="wb+", suffix=instance["name"])
        # TODO: Check why python wget is raised and error with code 403
        response = requests.get(download_url, stream=True)
        with open(file.name, "wb") as f:
            length = int(response.headers.get("content-length"))
            chunk_size = 8192
            total_chunks = length // chunk_size + 1
            widgets = ["Downloading: ", progressbar.Bar("#")]
            bar = progressbar.ProgressBar(
                max_value=total_chunks, widgets=widgets
            ).start()
            for counter, chunk in enumerate(
                response.iter_content(chunk_size=chunk_size)
            ):
                f.write(chunk)
                bar.update(counter)
        logger.debug("Downloaded instance %s.", id, tags=LogTags.DATABASE)
        return file

    def _pages(
        self, url: furl, **kwargs
    ) -> Generator[PaginatedResponse, None, None]:
        next_page = kwargs["page"]
        while next_page:
            response = self._list(url, **kwargs)
            yield response
            next_page = (
                furl(response["next"]).query.params["page"]
                if response["next"]
                else None
            )
            kwargs["page"] = next_page

    def _list(self, url: furl, **kwargs) -> PaginatedResponse:
        params = self._parse_params(**kwargs)
        response = self._restclient.get(url, params=params)
        if response.is_error:
            raise RequestError(response.status_code, response.text)
        return response.json()

    def _create(
        self,
        resource_name: str,
        instance: Dict,
        files: Optional[Dict[str, str]] = None,
    ) -> Dict:
        logger.debug("Saving new instance", tags=LogTags.DATABASE)
        model_name = resource_name.lower()
        api_path = self._get_api_path(resource_name)
        url = self._base_url / api_path
        if model_name == "file":
            instance = self._create_file(instance, url)
        else:
            files_payload = (
                {key: open(value, "rb") for key, value in files.items()}
                if files
                else None
            )
            # TODO: Fix in API so here we only use data argument
            if files_payload:
                req_args = {"data": instance, "files": files_payload}
            else:
                req_args = {"json": instance}

            response = self._restclient.post(url, **req_args)
            if response.is_error:
                raise RequestError(response.status_code, response.text)
            instance = response.json()
        logger.debug(
            "Instance %s created", instance["id"], tags=LogTags.DATABASE
        )
        return instance

    def _update(
        self,
        resource_name: str,
        resource_id: str,
        instance: Dict,
        files: Optional[Dict[str, str]] = None,
    ) -> Dict:
        logger.debug("Saving instance %s", resource_id, tags=LogTags.DATABASE)
        model_name = resource_name.lower()
        api_path = self._get_api_path(resource_name)
        url = self._base_url / api_path / f"{resource_id}/"
        if model_name == "file":
            with open(instance["file"], "rb") as f:
                file = {"file": f}
                response = self._restclient.put(url, data=instance, files=file)
        else:
            files_payload = (
                {key: open(value, "rb") for key, value in files.items()}
                if files
                else None
            )

            # TODO: Fix in API so here we only use data argument
            if files_payload:
                req_args = {"data": instance, "files": files_payload}
            else:
                req_args = {"json": instance}

            response = self._restclient.put(url, **req_args)

        if response.is_error:
            raise RequestError(response.status_code, response.text)
        return response.json()

    def _create_file(self, instance: Dict, url: furl):
        response = self._restclient.post(url, data=instance)
        if response.is_error:
            raise RequestError(response.status_code, response.text)
        file_path = instance["file"]
        # Check is this is handled somewher
        created_instance = response.json()
        self._upload_file(created_instance, file_path=file_path)
        return created_instance

    def _upload_file(self, instance: Dict, file_path: str):
        api_path = self._get_api_path("file")
        resource_id = instance.get("id")
        url = self._base_url / api_path / f"{resource_id}/upload_url/"
        response = self._restclient.get(url)
        if response.is_error:
            raise RequestError(response.status_code, response.text)
        upload_url = response.json().get("url")
        file = open(file_path, "rb")
        file_name = instance["name"]
        with open(file_path, "rb") as fid:
            file = {"file": (file_name, fid)}
            response = requests.put(
                upload_url,
                files=file,
            )
            if response.ok:
                raise RequestError(response.status_code, response.text)
        logger.debug(
            "File uploaded succesfully %s.", resource_id, tags=LogTags.DATABASE
        )

    def upload(
        self,
        resource_name: str,
        instance: Dict,
        file_path: str,
        type_: Optional[str] = None,
    ):
        api_path = self._get_api_path(resource_name)
        resource_id = instance.get("id")
        params = {"type": type_} if type_ else {}
        url = self._base_url / api_path / f"{resource_id}/upload_url/"
        response = self._restclient.get(url, params=params)
        if response.is_error:
            raise RequestError(response.status_code, response.text)
        upload_url = response.json().get("url")
        with open(file_path, "rb") as fid:
            response = requests.put(
                upload_url,
                data=fid,
            )
            if not response.ok:
                raise RequestError(response.status_code, response.text)
        logger.debug(
            "File uploaded succesfully %s.", resource_id, tags=LogTags.DATABASE
        )

    @staticmethod
    def _get_api_path(resource_name: str) -> str:
        model_name = resource_name.lower()
        api_path = MODEL_NAME_MAP.get(model_name)
        if not api_path:
            raise InvalidModelName(model_name)
        return api_path
