import requests
from requests import Session
from typing import Dict, Union, List, Any, Optional

# TODO: check if this the right way to define expected DataType
DataType = Union[Dict, List, bytes, Any]

restclient = None


class SplightResponse(requests.Response):

    def raise_for_status(self):
        """Raises an HTTPError if the response status code indicates an error (4xx or 5xx).

        Args:
            response (SplightResponse): The response object to check for errors.

        Raises:
            HTTPError: If the response status code indicates an error.
        """
        return self.raise_for_status()


class SplightRestClient:
    """
    A REST client for making HTTP requests.

    # TODO: update docstring to clean the folling kwargs

    For each `SplightResClient` method kwargs could be:
        - params: (optional) Dictionary, list of tuples or bytes to
            send in the query string for the request.
        - data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the request.
        - json: (optional) A JSON serializable Python object to send in the
            body of the request.
        - headers: (optional) Dictionary of HTTP Headers to send with the
            request.
        - cookies: (optional) Dict or CookieJar object to send with the
            request.
        - files: (optional) Dictionary of ``'name': file-like-objects``
            (or ``{'name': file-tuple}``) for multipart encoding upload.
            ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``,
            3-tuple ``('filename', fileobj, 'content_type')``
            or a 4-tuple ``('filename', fileobj, 'content_type',
            custom_headers)``, where ``'content-type'`` is a string
            defining the content type of the given file and ``custom_headers``
            a dict-like object containing additional headers to add for the
            file.
        - auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
        - timeout: (optional) How many seconds to wait for the server to send 
            data before giving up, as a float, or a :ref:`(connect timeout,
            read timeout) <timeouts>` tuple.
        - timeout: float or tuple
        - allow_redirects: (optional) Boolean. Enable/disable
            GET/OPTIONS/POST/PUT/PATCH/DELETE/HEAD redirection. Defaults to
            ``True``.
        - proxies: (optional) Dictionary mapping protocol to the URL of the
            proxy.
        - verify: (optional) Either a boolean, in which case it controls
            whether we verify the server's TLS certificate, or a string, in
            which case it must be a path to a CA bundle to use. Defaults to
            ``True``.
        - stream: (optional) if ``False``, the response content will be
            immediately downloaded.
        - cert: (optional) if String, path to ssl client cert file (.pem).
            If Tuple, ('cert', 'key') pair.
    """

    def __init__(self):
        """Initialize the SplightRestClient.

        # TODO: check arguments
        """
        self._session = Session()
        # self.__dict__.update(**kwargs)

    @property
    def headers(self):
        # while using Session
        return self._session.headers

    def get(
        self, url: str, params: Optional[DataType] = None, **kwargs
    ) -> SplightResponse:
        """Send a GET request to the specified URL.

        Args:
            url (str): The URL to send the GET request to.
            params (DataType, optional): The query parameters for the GET
                request.
            **kwargs: Additional arguments to pass to the GET request,
                such as headers or authentication. To know available
                values, check class docstring.

        Returns:
            SplightResponse: The response from the GET request.
        """
        response = self._session.get(url, params=params, **kwargs)
        return response

    def options(self, url: str, **kwargs) -> SplightResponse:
        """Send an OPTIONS request to the specified URL.

        Args:
            url (str): The URL to send the OPTIONS request to.
            **kwargs: Additional arguments to pass to the OPTIONS request,
                such as headers or authentication. To know available
                values, check class docstring.

        Returns:
            SplightResponse: The response from the OPTIONS request.
        """
        response = self._session.options(url, **kwargs)
        return response

    def head(self, url: str, **kwargs) -> SplightResponse:
        """Send a HEAD request to the specified URL.

        Args:
            url (str): The URL to send the HEAD request to.
            **kwargs: Additional arguments to pass to the HEAD request,
                such as headers or authentication. To know available
                values, check class docstring.

        Returns:
            SplightResponse: The response from the HEAD request.
        """
        response = self._session.head(url, **kwargs)
        return response

    def post(
        self,
        url: str,
        data: Optional[DataType] = None,
        json: Optional[Dict] = None,
        **kwargs
    ) -> SplightResponse:
        """Send a POST request to the specified URL.

        # TODO: check data type, and json type (itsn't dict)

        Args:
            url (str): The URL to send the POST request to.
            data (DataType, optional): The data to send in the POST request.
            json (dict, optional): Dictionary, list of tuples, bytes, or
                file-like object to send in the POST request body.
            **kwargs: Additional arguments to pass to the POST request,
                such as headers or authentication. To know available
                values, check class docstring.

        Returns:
            SplightResponse: The response from the POST request.
        """
        response = self._session.post(url, data=data, json=json, **kwargs)
        return response

    def put(
        self,
        url: str,
        data: Optional[DataType] = None,
        **kwargs
    ) -> SplightResponse:
        """Send a PUT request to the specified URL.

        Args:
            url (str): The URL to send the PUT request to.
            data (DataType, optional): The data to send in the PUT request.
            **kwargs: Additional arguments to pass to the PUT request,
                such as headers or authentication. To know available
                values, check class docstring.

        Returns:
            SplightResponse: The response from the PUT request.
        """
        response = self._session.put(url, data=data, **kwargs)
        return response

    def patch(
        self,
        url: str,
        data: Optional[DataType] = None,
        **kwargs
    ) -> SplightResponse:
        """Send a PATCH request to the specified URL.

        Args:
            url (str): The URL to send the PATCH request to.
            data (DataType, optional): The data to send in the PATCH request.
            **kwargs: Additional arguments to pass to the PATCH request,
                such as headers or authentication. To know available
                values, check class docstring.

        Returns:
            SplightResponse: The response from the PATCH request.
        """
        response = self._session.patch(url, data=data, **kwargs)
        return response

    def delete(self, url: str, **kwargs) -> SplightResponse:
        """Send a DELETE request to the specified URL.

        Args:
            url (str): The URL to send the DELETE request to.
            **kwargs: Additional arguments to pass to the DELETE request,
                such as headers or authentication. To know available
                values, check class docstring.

        Returns:
            SplightResponse: The response from the DELETE request.
        """
        response = self._session.delete(url, **kwargs)
        return response


def get_restclient():
    # uses restclient singleton
    if restclient is None:
        restclient = SplightRestClient()
    return restclient
