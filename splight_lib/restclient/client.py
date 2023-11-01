from typing import Any, Callable, List, Mapping, Optional, Union

import httpx

from splight_lib.restclient.types import (
    DEFAULT_LIMITS,
    DEFAULT_MAX_REDIRECTS,
    DEFAULT_TIMEOUT_CONFIG,
    AuthTypes,
    BaseTransport,
    CertTypes,
    CookieTypes,
    EventHook,
    HeaderTypes,
    Limits,
    ProxiesTypes,
    QueryParamTypes,
    RequestData,
    RequestFiles,
    TimeoutTypes,
    URLTypes,
    VerifyTypes,
)


class DefaultClient(httpx._client.UseClientDefault):
    """
    For some parameters such as `auth=...` and `timeout=...` we need to be able
    to indicate the default "unset" state, in a way that is distinctly different
    to using `None`.

    The default "unset" state indicates that whatever default is set on the
    client should be used. This is different to setting `None`, which
    explicitly disables the parameter, possibly overriding a client default.

    For example we use `timeout=DEFAULT_CLIENT`. Omitting the `timeout`
    parameter will send a request using whatever default timeout has been
    configured on the client. Including `timeout=None` will ensure no timeout is
    used.

    Note that user code shouldn't need to use the `DEFAULT_CLIENT` constant,
    but it is used internally when a parameter is not included.
    """

    # Currently, this class is a copy of httpx._client.UseClientDefault.


DEFAULT_CLIENT = DefaultClient()


class SplightResponse(httpx.Response):
    # Currently, this class is a copy of httpx.Response.

    @classmethod
    def from_response(cls, response: httpx.Response) -> "SplightResponse":
        obj_cls = cls(status_code=response.status_code)
        # copy attributes created out of __init__
        # we need a runtime copy not just attributes create at initialization
        for attr in response.__dict__.keys():
            response_attr = getattr(response, attr)
            setattr(obj_cls, attr, response_attr)

        return obj_cls


class SplightRestClient:
    """A REST client for making HTTP requests.

    Currently, this client is based on httpx.Client.

    Class initialization parameters.

    1. Compatible with requests interface.
    * verify (optional) SSL certificates (a.k.a CA bundle) used to verify the
    identity of requested hosts. Either `True` (default CA bundle), a path to an
    SSL certificate file, an `ssl.SSLContext`, or `False` (which will disable
    verification).
    * cert (optional) An SSL certificate used by the requested host to
    authenticate the client. Either a path to an SSL certificate file, or
    two-tuple of (certificate file, key file), or a three-tuple of (certificate
    file, key file, password).
    * proxies (optional) A dictionary mapping proxy keys to proxy URLs.
    * allow_redirects (optional) If set, automatically follow redirects. Default
    False.

    2. Added by httpx.
    * http1 (optional) To use HTTP1 protocol.
    * http2 (optional) To use HTTP2 protocol.
    * base_url (optional) A URL to use as the base when building request URLs.
    * limits (optional) The limits for transport configuration to use.
    Parameters for Limits class are: max_connections and
    max_keepalive_connections
    * max_redirects (optional) The maximum number of redirect responses that
    should be followed.
    * transport (optional) A transport class to use for sending requests over
    the network.
    * app (optional) An WSGI application to send requests to, rather than
    sending actual network requests.
    * trust_env (optional) Enables or disables usage of environment variables
    for configuration.
    * default_encoding (optional) The default encoding to use for decoding
    response text, if no charset information is included in a response
    Content-Type header. Set to a callable for automatic character set
    detection. Default: "utf-8".
    * event_hooks: used to run hooks for requests and responses.

    For ALL client methods. (Compatible with requests interface)
    * url URL to send the request.
    * auth (optional) An authentication class to use when sending requests.
    * params (optional) Query parameters to include in request URLs, as a
    string, dictionary, or sequence of two-tuples.
    * headers (optional) Dictionary of HTTP headers to include when sending
    requests.
    * cookies (optional) Dictionary of Cookie items to include when sending
    requests.
    * timeout (optional) The timeout configuration to use when sending requests.

    For POST, PUT and PATCH methods. (Compatible with requests interface)
    * data (optional) Dictionary, list of tuples, bytes, or file-like object to
    send in the body of the request.
    * files (optional) Iterable of files to send into the request.
    * json (optional) A JSON serializable Python object to send in the request
    body.
    """

    _GET_METHOD = "GET"
    _OPTIONS_METHOD = "OPTIONS"
    _HEAD_METHOD = "HEAD"
    _POST_METHOD = "POST"
    _PUT_METHOD = "PUT"
    _PATCH_METHOD = "PATCH"
    _DELETE_METHOD = "DELETE"

    def __init__(
        self,
        *,
        # params compatibles with requests interface
        auth: Optional[AuthTypes] = None,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
        verify: VerifyTypes = True,
        cert: Optional[CertTypes] = None,
        proxies: Optional[ProxiesTypes] = None,
        allow_redirects: bool = False,
        # extra params defined in httpx (not in requests)
        http1: bool = True,
        http2: bool = False,
        base_url: str = "",
        limits: Limits = DEFAULT_LIMITS,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        transport: Optional[BaseTransport] = None,
        app: Optional[Callable[..., Any]] = None,
        trust_env: bool = True,
        default_encoding: Union[str, Callable[[bytes], str]] = "utf-8",
        event_hooks: Optional[Mapping[str, List[EventHook]]] = None,
    ):
        """Initialize the SplightRestClient.

        Parameters: See class docstring.
        """
        # Client is the httpx Session impl
        # in httpx.Client allow_redirects is named follow_redirects
        self._client = httpx.Client(
            auth=auth,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            verify=verify,
            cert=cert,
            http1=http1,
            http2=http2,
            proxies=proxies,
            follow_redirects=allow_redirects,
            base_url=base_url,
            limits=limits,
            max_redirects=max_redirects,
            transport=transport,
            app=app,
            trust_env=trust_env,
            default_encoding=default_encoding,
            event_hooks=event_hooks,
        )
        self._async_client = httpx.AsyncClient(
            auth=auth,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            verify=verify,
            cert=cert,
            http1=http1,
            http2=http2,
            proxies=proxies,
            follow_redirects=allow_redirects,
            base_url=base_url,
            limits=limits,
            max_redirects=max_redirects,
            transport=transport,
            app=app,
            trust_env=trust_env,
            default_encoding=default_encoding,
            event_hooks=event_hooks,
        )

    def update_headers(self, new_headers: HeaderTypes):
        self._client.headers = self._client._merge_headers(new_headers)
        self._async_client.headers = self._async_client._merge_headers(
            new_headers
        )

    def get(
        self,
        url: URLTypes,
        *,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        auth: Union[AuthTypes, DefaultClient] = DEFAULT_CLIENT,
        allow_redirects: Union[bool, DefaultClient] = DEFAULT_CLIENT,
        timeout: Union[TimeoutTypes, DefaultClient] = DEFAULT_CLIENT,
    ) -> SplightResponse:
        """Send a GET request to the specified URL.

        Parameters: See class docstring.
        """
        raw_response = self._client.request(
            self._GET_METHOD,
            str(url),
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=allow_redirects,
            timeout=timeout,
        )
        return SplightResponse.from_response(raw_response)

    async def async_get(
        self,
        url: URLTypes,
        *,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        auth: Union[AuthTypes, DefaultClient] = DEFAULT_CLIENT,
        allow_redirects: Union[bool, DefaultClient] = DEFAULT_CLIENT,
        timeout: Union[TimeoutTypes, DefaultClient] = DEFAULT_CLIENT,
    ) -> SplightResponse:
        """Send a GET request to the specified URL.

        Parameters: See class docstring.
        """
        raw_response = await self._async_client.request(
            self._GET_METHOD,
            str(url),
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=allow_redirects,
            timeout=timeout,
        )
        return SplightResponse.from_response(raw_response)

    def options(
        self,
        url: URLTypes,
        *,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        auth: Union[AuthTypes, DefaultClient] = DEFAULT_CLIENT,
        allow_redirects: Union[bool, DefaultClient] = DEFAULT_CLIENT,
        timeout: Union[TimeoutTypes, DefaultClient] = DEFAULT_CLIENT,
    ) -> SplightResponse:
        """Send an OPTIONS request to the specified URL.

        Parameters: See class docstring.
        """
        raw_response = self._client.request(
            self._OPTIONS_METHOD,
            str(url),
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=allow_redirects,
            timeout=timeout,
        )
        return SplightResponse.from_response(raw_response)

    def head(
        self,
        url: URLTypes,
        *,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        auth: Union[AuthTypes, DefaultClient] = DEFAULT_CLIENT,
        allow_redirects: Union[bool, DefaultClient] = DEFAULT_CLIENT,
        timeout: Union[TimeoutTypes, DefaultClient] = DEFAULT_CLIENT,
    ) -> SplightResponse:
        """Send a HEAD request to the specified URL.

        Parameters: See class docstring.
        """
        raw_response = self._client.request(
            self._HEAD_METHOD,
            str(url),
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=allow_redirects,
            timeout=timeout,
        )
        return SplightResponse.from_response(raw_response)

    def post(
        self,
        url: URLTypes,
        *,
        data: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        json: Optional[Any] = None,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        auth: Union[AuthTypes, DefaultClient] = DEFAULT_CLIENT,
        allow_redirects: Union[bool, DefaultClient] = DEFAULT_CLIENT,
        timeout: Union[TimeoutTypes, DefaultClient] = DEFAULT_CLIENT,
    ) -> SplightResponse:
        """Send a POST request to the specified URL.

        Parameters: See class docstring.
        """
        raw_response = self._client.request(
            self._POST_METHOD,
            str(url),
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=allow_redirects,
            timeout=timeout,
        )
        return SplightResponse.from_response(raw_response)

    async def async_post(
        self,
        url: URLTypes,
        *,
        data: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        json: Optional[Any] = None,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        auth: Union[AuthTypes, DefaultClient] = DEFAULT_CLIENT,
        allow_redirects: Union[bool, DefaultClient] = DEFAULT_CLIENT,
        timeout: Union[TimeoutTypes, DefaultClient] = DEFAULT_CLIENT,
    ) -> SplightResponse:
        """Send a POST request to the specified URL.

        Parameters: See class docstring.
        """
        raw_response = await self._async_client.request(
            self._POST_METHOD,
            str(url),
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=allow_redirects,
            timeout=timeout,
        )
        return SplightResponse.from_response(raw_response)

    def put(
        self,
        url: URLTypes,
        *,
        data: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        json: Optional[Any] = None,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        auth: Union[AuthTypes, DefaultClient] = DEFAULT_CLIENT,
        allow_redirects: Union[bool, DefaultClient] = DEFAULT_CLIENT,
        timeout: Union[TimeoutTypes, DefaultClient] = DEFAULT_CLIENT,
    ) -> SplightResponse:
        """Send a PUT request to the specified URL.

        Parameters: See class docstring.
        """
        raw_response = self._client.request(
            self._PUT_METHOD,
            str(url),
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=allow_redirects,
            timeout=timeout,
        )
        return SplightResponse.from_response(raw_response)

    def patch(
        self,
        url: URLTypes,
        *,
        data: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        json: Optional[Any] = None,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        auth: Union[AuthTypes, DefaultClient] = DEFAULT_CLIENT,
        allow_redirects: Union[bool, DefaultClient] = DEFAULT_CLIENT,
        timeout: Union[TimeoutTypes, DefaultClient] = DEFAULT_CLIENT,
    ) -> SplightResponse:
        """Send a PATCH request to the specified URL.

        Parameters: See class docstring.
        """
        raw_response = self._client.request(
            self._PATCH_METHOD,
            str(url),
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=allow_redirects,
            timeout=timeout,
        )
        return SplightResponse.from_response(raw_response)

    def delete(
        self,
        url: URLTypes,
        *,
        data: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        json: Optional[Any] = None,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        auth: Union[AuthTypes, DefaultClient] = DEFAULT_CLIENT,
        allow_redirects: Union[bool, DefaultClient] = DEFAULT_CLIENT,
        timeout: Union[TimeoutTypes, DefaultClient] = DEFAULT_CLIENT,
    ) -> SplightResponse:
        """Send a DELETE request to the specified URL.

        Parameters: See class docstring.
        """
        raw_response = self._client.request(
            self._DELETE_METHOD,
            str(url),
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=allow_redirects,
            timeout=timeout,
        )
        return SplightResponse.from_response(raw_response)
