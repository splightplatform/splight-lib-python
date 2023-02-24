import json
from .classmap import CLASSMAP
from retry import retry
from splight_abstract.remote import AbstractRemoteClient
from splight_abstract.database import AbstractDatabaseClient
from splight_models import File
from remote_splight_lib.settings import settings
from remote_splight_lib.exceptions import InvalidModel
from remote_splight_lib.auth import SplightAuthToken
from splight_lib.encryption import EncryptionClient
from typing import Dict, List, Type

from furl import furl
from pydantic import BaseModel
from requests import Session
from requests.exceptions import (
    ConnectionError,
    Timeout
)
from tempfile import NamedTemporaryFile


REQUEST_EXCEPTIONS = (ConnectionError, Timeout)


class DatabaseClient(AbstractDatabaseClient, AbstractRemoteClient):
    """Splight API Database Client.
    Responsible for interacting with database resources using HTTP requests
    to the Splight API.
    """

    def __init__(self, namespace: str = "default"):
        super(DatabaseClient, self).__init__(namespace=namespace)
        self._base_url = furl(settings.SPLIGHT_PLATFORM_API_HOST)
        token = SplightAuthToken(
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
        )
        self._session = Session()
        self._session.headers.update(token.header)

    @retry(REQUEST_EXCEPTIONS, tries=3, delay=1)
    def save(self, instance: BaseModel) -> BaseModel:
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
        constructor = type(instance)
        model_data = self._get_model_data(constructor)

        path = model_data["path"]
        if instance.id:
            output = self._update(path, instance.id, instance)
        else:
            output = self._create(path, instance)
            instance.id = output["id"]
        return constructor.parse_obj(output)

    @retry(REQUEST_EXCEPTIONS, tries=3, delay=1)
    def delete(self, resource_type: Type, id: str):
        """Deletes a resource from the database

        Parameters
        ----------
        resource_type : Type
            The resource type to be deleted
        id : str
            The resource's id.

        Raises
        ------
        InvalidModel thrown when the model name is not correct.
        """
        model_data = self._get_model_data(resource_type)
        path = model_data["path"]
        url = self._base_url / f"{path}/{id}/"
        response = self._session.delete(url)
        response.raise_for_status()

    @retry(REQUEST_EXCEPTIONS, tries=3, delay=1)
    def _get(
        self,
        resource_type: Type,
        first: bool = False,
        limit_: int = -1,
        skip_: int = 0,
        page_size: int = -1,
        deleted: bool = False,
        **kwargs,
    ) -> List[BaseModel]:
        model_data = self._get_model_data(resource_type)
        path = model_data["path"]
        response = self._list(
            path,
            limit_=limit_,
            skip_=skip_,
            deleted=deleted,
            page_size=page_size,
            **kwargs,
        )
        parsed = [
            resource_type.parse_obj(resource)
            for resource in response["results"]
        ]
        if first:
            return parsed[0] if parsed else None
        return parsed

    @retry(REQUEST_EXCEPTIONS, tries=3, delay=1)
    def count(self, resource_type: Type, **kwargs) -> int:
        """Returns the number of resources in the database for a given model

        Parameters
        ----------
        resource_type : str
            The model name

        Returns
        -------
        int

        Raises
        ------
        InvalidModel thrown when the model name is not correct.
        """
        model_data = self._get_model_data(resource_type)
        path = model_data["path"]
        kwargs["page"] = 1  # Always start from the first page
        response = self._list(path, **kwargs)
        return response["count"]

    @retry(REQUEST_EXCEPTIONS, tries=3, delay=1)
    def download(self, instance: BaseModel, decrypt: bool = True, **kwargs) -> NamedTemporaryFile:
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
        constructor = type(instance)
        model_data = self._get_model_data(constructor)
        path = model_data["path"]
        url = self._base_url / f"{path}/{instance.id}/download"
        response = self._session.get(url)
        response.raise_for_status()
        f = NamedTemporaryFile("wb+")
        f.write(response.content)
        f.seek(0)
        if decrypt and instance.encrypted:
            encryption_manager = EncryptionClient()
            encryption_manager.decrypt_file(path=f.name)
        return f

    def _pages(self, path: str, **kwargs):
        next_page = kwargs["page"]
        while next_page:
            response = self._list(path, **kwargs)
            yield response
            next_page = (
                response["next"].split("page=")[1]
                if response["next"]
                else None
            )
            kwargs["page"] = next_page

    def _list(self, path: str, **kwargs):
        url = self._base_url / f"{path}/"
        params = self._parse_params(**kwargs)
        response = self._session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _get_model_data(constructor: Type):
        model_data = CLASSMAP.get(constructor)
        if not model_data:
            raise InvalidModel(constructor.schema()["title"])
        return model_data

    def _create(self, path: str, instance: BaseModel) -> Dict:
        url = self._base_url / f"{path}/"
        data = json.loads(instance.json(exclude_none=True))
        if isinstance(instance, File):
            with open(instance.file, 'rb') as f:
                file = {"file": f}
                response = self._session.post(url, data=data, files=file)
        else:
            response = self._session.post(url, json=data)

        response.raise_for_status()
        return response.json()

    def _update(self, path: str, resource_id: str, data: BaseModel) -> Dict:
        url = self._base_url / f"{path}/{resource_id}/"
        response = self._session.put(
            url, json=json.loads(data.json(exclude_none=True))
        )
        response.raise_for_status()
        return response.json()
