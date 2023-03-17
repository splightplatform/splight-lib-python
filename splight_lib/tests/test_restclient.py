import pytest
import requests
from requests import Session

from splight_lib.restclient.client import SplightRestClient

    
@pytest.mark.skip
def test_get_method_have_equal_response():
    url = ""
    kwargs = {}
    expected_response = {}

    _requests = requests
    _session = Session()
    _resclient = SplightRestClient()

    requests_response = _requests.get(url, kwargs).json()
    session_response = _session.get(url, kwargs).json()
    restclient_response = _resclient.get(url, kwargs).json()

    assert (
        expected_response == requests_response ==
        session_response == restclient_response
    )


@pytest.mark.skip
def test_options_method_have_equal_response():
    url = ""
    kwargs = {}
    expected_response = {}

    _requests = requests
    _session = Session()
    _resclient = SplightRestClient()

    requests_response = _requests.options(url, kwargs).json()
    session_response = _session.options(url, kwargs).json()
    restclient_response = _resclient.options(url, kwargs).json()

    assert (
        expected_response == requests_response ==
        session_response == restclient_response
    )
