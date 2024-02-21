"""
Type definitions for type checking purposes.
"""

import ssl
from http.cookiejar import CookieJar
from typing import (
    IO,
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from furl import furl
from httpx._auth import Auth
from httpx._config import Limits, Proxy, Timeout
from httpx._models import Cookies, Headers, Request
from httpx._urls import QueryParams

# Currently, this types are based on httpx._types.

DEFAULT_TIMEOUT_CONFIG = Timeout(timeout=60.0)
DEFAULT_LIMITS = Limits(max_connections=100, max_keepalive_connections=20)
DEFAULT_MAX_REDIRECTS = 20

PrimitiveData = Optional[Union[str, int, float, bool]]

AuthTypes = Union[
    Tuple[Union[str, bytes], Union[str, bytes]],
    Callable[["Request"], "Request"],
    "Auth",
]

QueryParamTypes = Union[
    "QueryParams",
    Mapping[str, Union[PrimitiveData, Sequence[PrimitiveData]]],
    List[Tuple[str, PrimitiveData]],
    Tuple[Tuple[str, PrimitiveData], ...],
    str,
    bytes,
]

HeaderTypes = Union[
    "Headers",
    Mapping[str, str],
    Mapping[bytes, bytes],
    Sequence[Tuple[str, str]],
    Sequence[Tuple[bytes, bytes]],
]

CookieTypes = Union[
    "Cookies", CookieJar, Dict[str, str], List[Tuple[str, str]]
]

TimeoutTypes = Union[
    Optional[float],
    Tuple[Optional[float], Optional[float], Optional[float], Optional[float]],
    "Timeout",
]

VerifyTypes = Union[str, bool, ssl.SSLContext]

CertTypes = Union[
    # certfile
    str,
    # (certfile, keyfile)
    Tuple[str, Optional[str]],
    # (certfile, keyfile, password)
    Tuple[str, Optional[str], Optional[str]],
]

# for now is just a string. In the future could be httpx._urls.URL too.
URLTypes = Union[str, furl]

ProxiesTypes = Union[
    URLTypes, "Proxy", Dict[URLTypes, Union[None, URLTypes, "Proxy"]]
]

EventHook = Callable[..., Any]

RequestData = Mapping[str, Any]

FileContent = Union[IO[bytes], bytes, str]

FileTypes = Union[
    # file (or bytes)
    FileContent,
    # (filename, file (or bytes))
    Tuple[Optional[str], FileContent],
    # (filename, file (or bytes), content_type)
    Tuple[Optional[str], FileContent, Optional[str]],
    # (filename, file (or bytes), content_type, headers)
    Tuple[Optional[str], FileContent, Optional[str], Mapping[str, str]],
]

RequestFiles = Union[Mapping[str, FileTypes], Sequence[Tuple[str, FileTypes]]]
