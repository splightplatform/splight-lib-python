import pytest
import requests
from httpx import Client
from requests import Session

from splight_lib.restclient import SplightRestClient


# This is an integration test. To run it, remove decorator
@pytest.mark.skip
@pytest.mark.parametrize(
    "method", ["get", "options", "head", "post", "put", "patch", "delete"]
)
@pytest.mark.parametrize("attr", ["status_code", "text", "content", "cookies"])
def test_all_splight_restclient_methods_have_equal_response_to_other_libraries(
    method, attr
):
    url = "https://jsonplaceholder.typicode.com/posts"
    _restclient = SplightRestClient()
    _httpx = Client()
    _session = Session()
    _requests = requests

    restclient_response = getattr(_restclient, method)(url)
    httpx_response = getattr(_httpx, method)(url)
    session_response = getattr(_session, method)(url)
    requests_response = getattr(_requests, method)(url)

    assert (
        getattr(restclient_response, attr)
        == getattr(httpx_response, attr)
        == getattr(session_response, attr)
        == getattr(requests_response, attr)
    ), f"Error in {attr} atributte."
