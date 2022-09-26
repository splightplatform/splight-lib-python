from furl import furl
from pydantic import BaseModel
from typing import Dict, Optional, Type, List
from requests import Session
from splight_abstract.storage import AbstractStorageClient
from remote_splight_lib.auth.auth import SplightAuthToken
from remote_splight_lib.settings import settings
from remote_splight_lib.exceptions import InvalidModel
from remote_splight_lib.storage.classmap import CLASSMAP
from splight_abstract.remote import AbstractRemoteClient


class StorageClient(AbstractStorageClient, AbstractRemoteClient):
    """Splight API Storage Client.
    Responsible for interacting with storage resources using HTTP requests
    to the Splight API.
    """

    def __init__(
        self,
        namespace: str = "default"
    ):
        """Class constructor

        Parameters
        ----------
        base_url : Union[str, furl]
            The URL for the Slight API
        token : Optional[SplightAuthToken]
            Instance of SplightAuthToken
        """
        super(StorageClient, self).__init__(namespace=namespace)
        self._base_url = furl(settings.SPLIGHT_PLATFORM_API_HOST)
        token = SplightAuthToken(
            access_key=settings.SPLIGHT_ACCESS_ID,
            secret_key=settings.SPLIGHT_SECRET_KEY,
        )
        self._session = Session()
        self._session.headers.update(token.header)

    @staticmethod
    def _get_model_data(constructor: Type):
        model_data = CLASSMAP.get(constructor)
        if not model_data:
            raise InvalidModel(constructor.schema()["title"])
        return model_data

    def _list(self, path: str, **kwargs):
        url = self._base_url / f"{path}/"
        params = self._parse_params(**kwargs)
        response = self._session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def _create(self, path: str, data: BaseModel) -> Dict:
        url = self._base_url / f"{path}/"
        response = self._session.post(url, json=data.dict())
        response.raise_for_status()
        return response.json()

    def _update(self, path: str, resource_id: str, data: BaseModel) -> Dict:
        url = self._base_url / f"{path}/{resource_id}/"
        response = self._session.put(url, json=data.dict())
        response.raise_for_status()
        return response.json()

    def _get(self, resource_type: Type, first=False, prefix: Optional[str] = None, limit_: int = -1, skip_: int = 0, **kwargs) -> List[BaseModel]:
        model_data = self._get_model_data(resource_type)
        path = model_data["path"]
        response = self._list(
            path,
            first=first,
            limit_=limit_,
            skip_=skip_,
            **kwargs,
        )
        parsed = [
            resource_type.parse_obj(resource)
            for resource in response["results"]
        ]
        return parsed

    def save(self, instance: BaseModel) -> BaseModel:
        raise NotImplementedError

    def copy(self, old_name: str, new_name: str):
        raise NotImplementedError

    def delete(self, resource_type: Type, id: str):
        raise NotImplementedError

    def download(self, resource_type: Type, id: str, target: str) -> str:
        model_data = self._get_model_data(resource_type)
        path = model_data["path"]
        url = self._base_url / f"{path}/{id}/download"
        response = self._session.get(url)
        response.raise_for_status()
        with open(target, "wb") as f:
            f.write(response.content)
        return response.content

    def get_temporary_link(self, filename: str, target: str) -> str:
        raise NotImplementedError
