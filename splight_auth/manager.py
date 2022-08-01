from requests import Session

from client import AbstractClient

from .endpoints.endpoint import (
    Credentials,
    Organizations,
    Profile,
    Roles,
    Users,
)


class MethodNotAllowed(Exception):
    def __init__(self, method: str):
        self._msg = f"Method {method} not valid"

    def __str__(self) -> str:
        return self._msg


class AuthClient(AbstractClient):
    def __init__(self, url: str, headers):
        super().__init__()
        self._url = url

        session = Session()
        session.headers.update(headers)
        self.credentials = Credentials(base_url=self._url, session=session)
        self.profile = Profile(base_url=self._url, session=session)
        self.role = Roles(base_url=self._url, session=session)
        self.user = Users(base_url=self._url, session=session)
        self.organization = Organizations(base_url=self._url, session=session)


# class AuthManager:
#
#     _FORWARD_REQUEST_MAP = {
#         "DELETE": requests.delete,
#         "GET": requests.get,
#         "POST": requests.post,
#         "PUT": requests.put,
#         "PATCH": requests.patch,
#     }
#
#     def __init__(self, auth_url: str, path_prefix: Optional[str] = None):
#         self._auth_url = auth_url if auth_url.endswith("/") else f"{auth_url}/"
#         self._prefix = (
#             path_prefix if path_prefix.startswith("/") else f"/{path_prefix}"
#         )
#
#     def forward_request(self, request: Request) -> Tuple[Dict[str, Any], int]:
#         """Makes a request to the Auth API.
#
#         Parameters
#         ----------
#         request : Request
#             The request
#
#         Returns
#         -------
#         Tuple[Dict[str, Any], int]
#             The response of the requests
#         """
#         method = request.method
#
#         # if method not in self._FORWARD_REQUEST_MAP:
#         #     raise MethodNotAllowed(method)
#
#         path = (
#             request.path.replace(self._prefix, "")
#             if self._prefix
#             else request.path
#         )
#
#         headers = {
#             "Authorization": request.headers.get("Authorization"),
#             "X-Organization-ID": request.headers.get("X-Organization-ID"),
#         }
#         body = request.data if request.data else None
#         params = request.query_params if request.query_params else None
#         return self.make_request(
#             method, path, headers=headers, body=body, params=params
#         )
#         # response = self._FORWARD_REQUEST_MAP[method](
#         #     url,
#         #     headers=headers,
#         #     json=request.data,
#         #     params=request.query_params,
#         # )
#         # return response.json(), response.status_code
#
#     def make_request(
#         self,
#         method: str,
#         path: str,
#         headers: Optional[Dict] = None,
#         body: Optional[Dict] = None,
#         params: Optional[Dict] = None,
#     ):
#         if method not in self._FORWARD_REQUEST_MAP:
#             raise MethodNotAllowed(method)
#         url = f"{self._auth_url}{path}"
#         response = self._FORWARD_REQUEST_MAP[method](
#             url,
#             headers=headers,
#             json=body,
#             params=params
#         )
#         content = response.json() if response.content else None
#         return content, response.status_code
