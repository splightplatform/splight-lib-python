import requests
from typing import Dict, Union, List, Any


class SplightResponse(requests.Response):
    pass


class HTTPError(Exception):
    pass


class SplightRestClient:
    """
    A REST client for making HTTP requests.
    """

    def __init__(self, base_url):
        """Initialize the SplightRestClient with a base URL.

        Args:
            base_url (str): The base URL for the REST API.
        """
        self.base_url = base_url

    def raise_for_status(self, response: SplightResponse):
        """Raises an HTTPError if the response status code indicates an error (4xx or 5xx).

        Args:
            response (SplightResponse): The response object to check for errors.

        Raises:
            HTTPError: If the response status code indicates an error.
        """
        return response.raise_for_status()

    def get(self, path: str, params: Union[Dict, List] = None, **kwargs) -> SplightResponse:
        """Send a GET request to the specified path.

        # TODO: check params type

        Args:
            path (str): The path to send the GET request to.
            params (dict, optional): The query parameters for the GET request.
            **kwargs: Additional arguments to pass to the GET request, such as headers or authentication.

        Returns:
            SplightResponse: The response from the GET request.
        """
        url = self.base_url + path
        response = requests.get(url, params=params, **kwargs)
        return response

    def options(self, path: str, **kwargs) -> SplightResponse:
        """Send an OPTIONS request to the specified URL.

        Args:
            path (str): The path to send the OPTIONS request to.

        Returns:
            SplightResponse: The response from the OPTIONS request.
        """
        url = self.base_url + path
        response = requests.options(url, **kwargs)
        return response

    def head(self, path: str, **kwargs) -> SplightResponse:
        """Send a HEAD request to the specified URL.

        Args:
            path (str): The path to send the HEAD request to.

        Returns:
            SplightResponse: The response from the HEAD request.
        """
        url = self.base_url + path
        response = requests.head(url, **kwargs)
        return response

    def post(self, path: str, data: Union[Dict, List, bytes, Any] = None, json: dict = None, **kwargs) -> SplightResponse:
        """Send a POST request to the specified path.

        # TODO: check data type, and json type (itsn't dict)

        Args:
            path (str): The path to send the POST request to.
            data (dict, optional): The JSON data to send in the POST request.
            json (optional): Dictionary, list of tuples, bytes, or file-like
                object to send in the POST request body.
            **kwargs: Additional arguments to pass to the POST request, such as headers or authentication.

        Returns:
            SplightResponse: The response from the POST request.
        """
        url = self.base_url + path
        response = requests.post(url, data=data, json=json, **kwargs)
        return response

    def put(self, path: str, data: Union[Dict, List] = None, **kwargs) -> SplightResponse:
        """Send a PUT request to the specified path.

        # TODO: check data type

        Args:
            path (str): The path to send the PUT request to.
            data (dict, optional): The JSON data to send in the PUT request.
            **kwargs: Additional arguments to pass to the PUT request, such as headers or authentication.

        Returns:
            SplightResponse: The response from the PUT request.
        """
        url = self.base_url + path
        response = requests.put(url, json=data, **kwargs)
        return response

    def patch(self, path: str, data: Union[Dict, List] = None, **kwargs) -> SplightResponse:
        """Send a PATCH request to the specified path.

        # TODO: check data type

        Args:
            path (str): The path to send the PATCH request to.
            data (dict, optional): The JSON data to send in the PATCH request.
            **kwargs: Additional arguments to pass to the PATCH request, such as headers or authentication.

        Returns:
            SplightResponse: The response from the PATCH request.
        """
        url = self.base_url + path
        response = requests.patch(url, data=data, **kwargs)
        return response

    def delete(self, path: str, **kwargs) -> SplightResponse:
        """Send a DELETE request to the specified URL.

        Args:
            path (str): The path to send the DELETE request to.

        Returns:
            SplightResponse: The response from the DELETE request.
        """
        url = self.base_url + path
        response = requests.delete(url, **kwargs)
        return response
