from uuid import uuid4
from asyncio.log import logger
from typing import Any, Dict

from splight_abstract import AbstractAuthClient, QuerySet
from splight_models import User


class FakeCredentials:
    def count(self, *args, **kwargs):
        return self.list()[0]["count"]

    def get(self, *args, **kwargs) -> QuerySet:
        return QuerySet(self, *args, **kwargs)

    def _get(self, *args, **kwargs):
        return self.list()[0]["results"]

    def list(self):
        return (
            {
                "count": 3,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "access_id": "6f5c1652-c52d-4aea-bd9c-5bf72d63c5b6",
                        "created_date": "2022-07-05T18:02:32.692815Z",
                        "last_used": "2022-07-05T18:02:32.692824Z",
                        "user": 1,
                    },
                    {
                        "access_id": "01c5bc01-d0c6-43b1-91d2-698f80545c82",
                        "created_date": "2022-07-05T18:02:35.630840Z",
                        "last_used": "2022-07-05T18:02:35.630856Z",
                        "user": 1,
                    },
                    {
                        "access_id": "13e9294c-4810-4a8d-8452-61961c7e8ecd",
                        "created_date": "2022-07-05T18:02:36.916698Z",
                        "last_used": "2022-07-05T18:02:36.916708Z",
                        "user": 1,
                    },
                ],
            },
            200,
        )

    def create(self, data: Dict[str, Any]):
        secret_key = (
            "addffg5b024dbc7f6b6760012ea493e738e350fad0b19e02405342f6666fd513"
        )
        return (
            {
                "access_id": "57e45010-ad7a-4dce-b759-98ec4f77a079",
                "created_date": "2022-07-05T19:29:16.061270Z",
                "last_used": "2022-07-05T19:29:16.061282Z",
                "user": 1,
                "secret_key": secret_key,
            },
            201,
        )

    def destroy(self, resource_id: str):
        return ({}, 204)


class FakeDeployment:
    def list(self):
        return (
            {
                "count": 3,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "access_id": "6f5c1652-c52d-4aea-bd9c-5bf72d63c5b6",
                        "created_date": "2022-07-05T18:02:32.692815Z",
                        "last_used": "2022-07-05T18:02:32.692824Z",
                    },
                    {
                        "access_id": "01c5bc01-d0c6-43b1-91d2-698f80545c82",
                        "created_date": "2022-07-05T18:02:35.630840Z",
                        "last_used": "2022-07-05T18:02:35.630856Z",
                    },
                    {
                        "access_id": "13e9294c-4810-4a8d-8452-61961c7e8ecd",
                        "created_date": "2022-07-05T18:02:36.916698Z",
                        "last_used": "2022-07-05T18:02:36.916708Z",
                    },
                ],
            },
            200,
        )

    def create(self, data: Dict[str, Any]):
        secret_key = (
            "addffg5b024dbc7f6b6760012ea493e738e350fad0b19e02405342f6666fd513"
        )
        return (
            {
                "access_id": "57e45010-ad7a-4dce-b759-98ec4f77a079",
                "created_date": "2022-07-05T19:29:16.061270Z",
                "last_used": "2022-07-05T19:29:16.061282Z",
                "secret_key": secret_key,
            },
            201,
        )

    def destroy(self, resource_id: str):
        return ({}, 204)


class FakeProfile:
    def count(self, *args, **kwargs):
        return self.list()[0]["count"]

    def get(self, *args, **kwargs) -> QuerySet:
        return QuerySet(self, *args, **kwargs)

    def _get(self, *args, **kwargs):
        return self.list()[0]["results"]

    def list(self):
        return (
            {
                "organization_id": "org_gxUvmxKLxSZPtHH8",
                "original_organization_id": "org_gxUvmxKLxSZPtHH3",
                "user_id": "auth0|628f9e023211690069ccc193",
                "username": "fake.user",
                "name": "fake.user@splight-ae.com",
                "email": "fake.user@splight-ae.com",
                "picture": "https://s.gravatar.com/avatar/a7b54dab1cd2b75ec1b1a8f6ed31efdc?s=480&r=pg&d=https%3A%2F%2Fcdn.auth0.com%2Favatars%2Fma.png",
                "permissions": ["admin", "splightadmin"],
                "user_metadata": {
                    "language": "en",
                    "theme": "light",
                    "picture_color": "light-green",
                },
                "app_metadata": {"is_manager": True},
                "role": "splightadmin",
            },
            200,
        )

    def update_profile(self, data: Dict[str, Any]):
        return self.list()


class FakeOrganization:

    def count(self, *args, **kwargs):
        return self.list()[0]["count"]

    def get(self, *args, **kwargs) -> QuerySet:
        return QuerySet(self, *args, **kwargs)

    def _get(self, *args, **kwargs):
        return self.list()[0]

    def list(self):
        return (
            {
                "id": "org_fGMkta1hcU4NWkp1",
                "name": "splight",
                "display_name": "Splight",
                "metadata": {
                    "billing_id": "123",
                    "blockchain_id": (
                        "0xcCd6872568009c5669fc699098a4373171C905B6"
                    ),
                    "manager_email": "fake.user@splight-ae.com"
                },
            },
            200,
        )

    def update_metadata(self, data: Dict[str, Any]):
        return self.list()


class FakeRoles:

    def count(self, *args, **kwargs):
        return self.list()[0]["count"]

    def get(self, *args, **kwargs) -> QuerySet:
        return QuerySet(self, *args, **kwargs)

    def _get(self, *args, **kwargs):
        return self.list()[0]["results"]

    def list(self):
        return (
            {
                "count": 4,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "id": "rol_xYsOLG4Kni9I9EJF",
                        "name": "admin",
                        "description": None,
                        "permissions": [],
                    },
                    {
                        "id": "rol_GZEhX5vu4WbVWeM5",
                        "name": "editor",
                        "description": None,
                        "permissions": [],
                    },
                    {
                        "id": "rol_8O7rXRkdtRklGW28",
                        "name": "splightadmin",
                        "description": None,
                        "permissions": [],
                    },
                    {
                        "id": "rol_eKzFB2R4lqYxeF2K",
                        "name": "viewer",
                        "description": None,
                        "permissions": [],
                    },
                ],
            },
            200,
        )

    def retrieve(self, resource_id: str):
        return self.list()[0]["results"][0]


class FakeUsers:
    FAKE_USER_0 = {
        "user_id": "google-oauth2|109709194253657961436",
        "email": "maximiliano.pezzotta@splight-ae.com",
        "picture": (
            "https://lh3.googleusercontent.com/a/AATXAJx7mtKTKLwpBNLy0TOQJ0jK"
            "5Y2LMcbEzV4xQBNF=s96-c"
        ),
        "name": "Maximiliano Pezzotta",
        "app_metadata": {"is_manager": False},
        "user_metadata": {"theme": "dark", "theme": "dark"},
        "blocked": False,
        "roles": None,
        "role": None,
    }
    FAKE_USER_1 = {
        "user_id": "auth0|61571fb933f692007043a0aa",
        "email": "example@gmail.com",
        "picture": (
            "https://s.gravatar.com/avatar/e820bb4aba5ad74c5a6ff1aca16641f6?s"
            "=480&r=pg&d=https%3A%2F%2Fcdn.auth0.com%2Favatars%2Fex.png"
        ),
        "name": "example@gmail.com",
        "app_metadata": {"is_manager": False},
        "user_metadata": {},
        "blocked": False,
        "roles": None,
        "role": None,
    }
    FAKE_USER_2 = {
        "user_id": "google-oauth2|111755134701574065193",
        "email": "estrella.cholod@splight-ae.com",
        "picture": (
            "https://lh3.googleusercontent.com/a/AATXAJwi2Z-TlTLz96K6IPClNWef"
            "HNkAdu31RKAzSzxl=s96-c"
        ),
        "name": "Estrella Cholod",
        "app_metadata": {"is_manager": True},
        "user_metadata": {},
        "blocked": False,
        "roles": None,
        "role": None,
    }

    def count(self, *args, **kwargs):
        return self.list()[0]["count"]

    def get(self, *args, **kwargs) -> QuerySet:
        return QuerySet(self, *args, **kwargs)

    def _get(self, *args, **kwargs):
        return self.list()[0]["results"]

    def list(self):
        return (
            {
                "count": 3,
                "next": None,
                "previous": None,
                "results": [
                    self.FAKE_USER_0,
                    self.FAKE_USER_1,
                    self.FAKE_USER_2,
                ],
            },
            200,
        )

    def retrieve(self, resource_id: str):
        return (self.FAKE_USER_0, 200)

    def users_update(self, resource_id: str, data: Dict[str, Any]):
        return (self.FAKE_USER_1, 200)


class FakeInvitations:

    def count(self, *args, **kwargs):
        return self.list()[0]["count"]

    def get(self, *args, **kwargs) -> QuerySet:
        return QuerySet(self, *args, **kwargs)

    def _get(self, *args, **kwargs):
        return self.list()[0]["results"]

    def list(self):
        return (
            {
                "count": 2,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "id": "uinv_4SfR3ucBxOj3wpqG",
                        "client_id": "1IsJjtPUv1DgHqsfZX4YsEjEStRRu1SG",
                        "inviter": {"name": "matias.silva@splight-ae.com"},
                        "invitee": {
                            "email": "matias.silva+1234@splight-ae.com"
                        },
                        "app_metadata": {},
                        "user_metadata": {},
                        "invitation_url": "https://integrationapp.splight-ae.com/auth-redirect?orgInvitation=true&invitation=kyWlQxQdZrX4RegzIFKhqHBwUcCGEZAj&organization=org_gxUvmxKLxSZPtHH8&organization_name=splight",
                        "ticket_id": "kyWlQxQdZrX4RegzIFKhqHBwUcCGEZAj",
                        "created_at": "2022-08-04T19:34:59.300Z",
                        "expires_at": "2022-08-11T19:34:59.300Z",
                        "organization_id": "org_gxUvmxKLxSZPtHH8",
                        "roles": ["rol_xYsOLG4Kni9I9EJF"],
                    },
                    {
                        "id": "uinv_0mKqsA8TqAZi2hCU",
                        "client_id": "1IsJjtPUv1DgHqsfZX4YsEjEStRRu1SG",
                        "inviter": {"name": "matias.silva@splight-ae.com"},
                        "invitee": {"email": "matias.silva+5@splight-ae.com"},
                        "app_metadata": {},
                        "user_metadata": {},
                        "invitation_url": "https://integrationapp.splight-ae.com/auth-redirect?orgInvitation=true&invitation=oq54fST3OQt3rxX7DI5wIDQbfudzKD9J&organization=org_gxUvmxKLxSZPtHH8&organization_name=splight",
                        "ticket_id": "oq54fST3OQt3rxX7DI5wIDQbfudzKD9J",
                        "created_at": "2022-08-04T17:47:48.639Z",
                        "expires_at": "2022-08-11T17:47:48.639Z",
                        "organization_id": "org_gxUvmxKLxSZPtHH8",
                        "roles": ["rol_xYsOLG4Kni9I9EJF"],
                    },
                ],
            },
            200,
        )

    def invitations_create(self, data: Dict[str, Any]):
        return (
            {
                "id": "asd",
                "client_id": "asd",
                "inviter": {"name": "fake.user@splight-ae.com"},
                "invitee": {"email": "fake.user+15@splight-ae.com"},
                "app_metadata": {},
                "user_metadata": {},
                "invitation_url": "https://integrationapp.splight-ae.com/",
                "ticket_id": "5qGQxSZJs9sQGDzmG1xAWhzTo0eabKVA",
                "created_at": "2022-07-05T19:37:48.367Z",
                "expires_at": "2022-07-12T19:37:48.367Z",
                "organization_id": "orgsUvmxKLxSZPtHH8",
            },
            201,
        )


class FakeOrganizations:

    def count(self, *args, **kwargs):
        return self.list()[0]["count"]

    def get(self, *args, **kwargs) -> QuerySet:
        return QuerySet(self, *args, **kwargs)

    def _get(self, *args, **kwargs):
        return self.list()[0]["results"]

    def list(self):
        return (
            {
                "count": 3,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "id": "org_gxUvmxKLxSZPtHH8",
                        "name": "splight",
                        "display_name": "Splight",
                        "metadata": {
                            "billing_id": "123",
                            "blockchain_id": (
                                "0xad087302625aD69609248554B507dBE22B129F96"
                            ),
                        },
                    },
                    {
                        "id": "org_qgoGDtof5MnwzzMe",
                        "name": "organization_test",
                        "display_name": "Organization_test",
                        "metadata": {
                            "billing_id": None,
                            "blockchain_id": None,
                        },
                    },
                    {
                        "id": "org_HhMefMw2ioFGDJqw",
                        "name": "integration_splight",
                        "display_name": "Integration_splight",
                        "metadata": {
                            "billing_id": None,
                            "blockchain_id": None,
                        },
                    },
                ],
            },
            200,
        )

    def retrieve(self, resource_id: str):
        return (
            {
                "id": "org_HhMefMw2ioFGDJqw",
                "name": "integration_splight",
                "display_name": "Integration_splight",
                "metadata": {
                    "billing_id": None,
                    "blockchain_id": None,
                },
            },
            200,
        )

    def update(self, resource_id: str, data: Dict[str, Any]):
        return (
            {
                "id": "org_HhMefMw2ioFGDJqw",
                "name": "integration_splight",
                "display_name": "Integration_splight",
                "metadata": {
                    "billing_id": None,
                    "blockchain_id": None,
                },
            },
            200,
        )

    def invite_manager(self, organization_id: str, data: Dict[str, Any]):
        return ({}, 200)

    def create(self, data: Dict[str, Any]):
        logger.info("[FAKED] Created new org")
        data.update({"id": "org_HhMefMw2ioFGDJqw"})
        return data, 201

    def destroy(self, resource_id: str):
        logger.info("[FAKED] Deleted org {id}")
        pass


class FakeAuthClient(AbstractAuthClient):
    def __init__(self, *args, **kwargs):
        super().__init__()

        self._credentials = FakeCredentials()
        self._deployment = FakeDeployment()
        self._profile = FakeProfile()
        self._role = FakeRoles()
        self._user = FakeUsers()
        self._invitation = FakeInvitations()
        self._organization = FakeOrganization()
        self._organizations = FakeOrganizations()

    @property
    def credentials(self):
        return self._credentials

    @property
    def deployment(self):
        return self._deployment

    @property
    def profile(self):
        return self._profile

    @property
    def role(self):
        return self._role

    @property
    def user(self):
        return self._user

    @property
    def invitation(self):
        return self._invitation

    @property
    def organization(self):
        return self._organization

    @property
    def organizations(self):
        return self._organizations

    def authenticate(self):
        user_complete_info: Dict = {
            "organization_id": "org_gxUvmxKLxSZPtHH8",
            "original_organization_id": "org_gxUvmxKLxSZPtHH3",
            "user_id": "auth0|628f9e023211690069ccc193",
            "username": "fake.user",
            "name": "fake.user@splight-ae.com",
            "email": "fake.user@splight-ae.com",
            "picture": "https://s.gravatar.com/avatar/a7b54dab1cd2b75ec1b1a8f6ed31efdc?s=480&r=pg&d=https%3A%2F%2Fcdn.auth0.com%2Favatars%2Fma.png",
            "permissions": ["admin", "splightadmin"],
            "user_metadata": {
                "language": "en",
                "theme": "light",
                "picture_color": "light-green",
            },
            "app_metadata": {"is_manager": True},
            "role": "splightadmin",
        }
        user: User = User.parse_obj(user_complete_info)
        return (user, None)

    def authenticate_header(self):
        return "Bearer"
