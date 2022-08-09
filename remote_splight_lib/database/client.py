from typing import Dict, List, Optional, Type, Union

from furl import furl
from pydantic import BaseModel
from requests import Session

from remote_splight_lib.auth import SplightAuthToken
from remote_splight_lib.exceptions import InvalidModel
from splight_abstract.database import AbstractDatabaseClient

from .classmap import CLASSMAP


class DatabaseClient(AbstractDatabaseClient):
    """Splight API Database Client.
    Responsible for interacting with database resources using HTTP requests
    to the Splight API.
    """

    def __init__(
        self,
        base_url: Union[str, furl],
        token: Optional[SplightAuthToken] = None,
    ):
        """Class constructor

        Parameters
        ----------
        base_url : Union[str, furl]
            The URL for the Slight API
        token : Optional[SplightAuthToken]
            Instance of SplightAuthToken
        """
        self._base_url = (
            base_url if isinstance(base_url, furl) else furl(base_url)
        )
        self._session = Session()
        if token:
            self._session.headers.update(token.header)

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
        return constructor.parse_obj(output)

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

    def _get(
        self,
        resource_type: Type,
        first: bool = False,
        limit_: int = -1,
        skip_: int = 0,
        deleted: bool = False,
        **kwargs,
    ) -> List[BaseModel]:
        model_data = self._get_model_data(resource_type)
        path = model_data["path"]
        response = self._list(
            path,
            first=first,
            limit_=limit_,
            skip_=skip_,
            deleted=deleted,
            **kwargs,
        )
        parsed = [
            resource_type.parse_obj(resource)
            for resource in response["results"]
        ]
        return parsed

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

        count = 0
        for page in self._pages(path, **kwargs):
            count += len(page["results"])
        return count

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
        response = self._session.get(url, params=kwargs)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _get_model_data(constructor: Type):
        model_data = CLASSMAP.get(constructor)
        if not model_data:
            raise InvalidModel(constructor.schema()["title"])
        return model_data

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
