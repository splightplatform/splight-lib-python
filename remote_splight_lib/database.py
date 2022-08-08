from typing import Any, Dict, List, Optional, Union

from furl import furl
from requests import Session

from splight_models.base import SplightBaseModel

from .auth import SplightAuthToken
from .exceptions import InvalidModel

RESOURCES_MAPP = [
    "algorithm",
    "asset",
    "attribute",
    "connector",
    "deployment",
    "network",
    "rule",
    "storage",
]


class DatabaseClient:
    """Splight API Database Client.
    Responsible for interacting with database resources using HTTP requests
    to the Splight API.

    Methods
    -------
    save(model_name: str, data: SplightBaseModel)

    list(model_name):

    count(model_name):

    delete(model_name: str, resource_id: str)
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

    def save(self, model_name: str, data: SplightBaseModel) -> Dict:
        """Creates or updates a new resource depending on the model if
        it contains the id or not.

        Parameters
        ----------
        model_name : str
            The name of the model to be created or updated.
        data : SplightBaseModel
            The instance of the pydantic model.

        Returns
        -------
        Dict with the created or updated resource.

        Raises
        ------
        InvalidModel thrown when the model name is not correct.
        """
        if model_name not in RESOURCES_MAPP:
            raise InvalidModel(model_name)

        if data.id:
            output = self._update(model_name, data.id, data)
        else:
            output = self._create(model_name, data)
        return output

    def list(self, model_name: str) -> List[Dict]:
        """Lists all the resources for a given model

        Parameters
        ----------
        model_name : str
            The name of the resources to be listed

        Returns
        -------
        List[Dict] the list with the resources.

        Raises
        ------
        InvalidModel thrown when the model name is not correct.
        """
        if model_name not in RESOURCES_MAPP:
            raise InvalidModel(model_name)
        url = self._base_url / f"{model_name}/"
        response = self._session.get(url)
        response.raise_for_status()
        return response.json()["results"]

    def count(self, model_name: str) -> int:
        """Returns the number of resources in the database for a given model

        Parameters
        ----------
        model_name : str
            The model name

        Returns
        -------
        int

        Raises
        ------
        InvalidModel thrown when the model name is not correct.
        """
        if model_name not in RESOURCES_MAPP:
            raise InvalidModel(model_name)
        url = self._base_url / f"{model_name}/"
        response = self._session.get(url)
        response.raise_for_status()
        return response.json()["count"]

    def retrieve(self, model_name: str, resource_id: str) -> Dict:
        """Gets the resource defined by its id

        Parameters
        ----------
        model_name : str
            The model's name of the resource to be retrieved
        resource_id : str
            The resource's ID

        Returns
        -------
        Dict the resource's information.

        Raises
        ------
        InvalidModel thrown when the model name is not correct.
        """
        if model_name not in RESOURCES_MAPP:
            raise InvalidModel(model_name)
        url = self._base_url / f"{model_name}/{resource_id}/"
        response = self._session.get(url)
        response.raise_for_status()
        return response.json()

    def delete(self, model_name: str, resource_id: str):
        """Deletes a resource from the database

        Parameters
        ----------
        model_name : str

        resource_id : str

        Raises
        ------
        InvalidModel thrown when the model name is not correct.
        """
        if model_name not in RESOURCES_MAPP:
            raise InvalidModel(model_name)
        url = self._base_url / f"{model_name}/{resource_id}/"
        response = self._session.delete(url)
        response.raise_for_status()

    def request(
        self,
        method: str,
        path: str,
        path_params: Dict[str, Any],
        data: Optional[SplightBaseModel] = None,
    ):
        """Makes a request to the Splight API

        Parameters
        ----------
        method : str
            HTTP method
        path : str
            Endpoint path with parameters
        path_params : Dict[str, Any]
            Dict of key, values pair for each parameter in the path
        data : Optional[SplightBaseModel]
            Pydantic model for the request body

        Returns
        -------
        Union[Dict, str]
        """
        url = self._base_url / path.format(**path_params)
        body = data.dict() if data else None
        response = self._session.request(method, url=url, json=body)
        response.raise_for_status()
        return response.json() if response.content else response.txt

    def _create(self, model_name: str, data: SplightBaseModel) -> Dict:
        url = self._base_url / f"{model_name}/"
        response = self._session.post(url, json=data.dict())
        response.raise_for_status()
        return response.json()

    def _update(
        self, model_name: str, resource_id: str, data: SplightBaseModel
    ):
        url = self._base_url / f"{model_name}/{resource_id}/"
        response = self._session.put(url, json=data.dict())
        response.raise_for_status()
        return response.json()
