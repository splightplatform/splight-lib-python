from typing import Any, Dict

from client import AbstractClient


class FakeCredentials:
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

    def delete(self, resource_id: str):
        return ({}, 204)


class FakeProfile:
    def list(self):
        return (
            {
                "organization_id": "org_gxUvmxKLxSZPtHH8",
                "user_id": "auth0|628f9e023211690069ccc193",
                "username": "fake.user",
                "name": "fake.user@splight-ae.com",
                "email": "fake.user@splight-ae.com",
                "picture": (
                    "https://s.gravatar.com/avatar/a7b54dab1cd2b75ec1b1a8f6ed"
                    "31efdc?s=480&r=pg&d=https%3A%2F%2Fcdn.auth0.com%2Favatars"
                    "%2Fma.png"
                ),
                "theme": "dark",
                "picture_color": "green-blue",
                "language": "es",
                "permissions": ["admin", "splightadmin"],
                "role": "splightadmin",
            },
            200,
        )

    def update_profile(self, data: Dict[str, Any]):
        return self.list()

    def organization(self):
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
                },
            },
            200,
        )

    def update_organization(self, data: Dict[str, Any]):
        return self.organization()


class FakeRoles:
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
        return self.list()["results"][0]


class FakeUsers:
    FAKE_USER_0 = {
        "user_id": "google-oauth2|109709194253657961436",
        "email": "maximiliano.pezzotta@splight-ae.com",
        "picture": (
            "https://lh3.googleusercontent.com/a/AATXAJx7mtKTKLwpBNLy0TOQJ0jK"
            "5Y2LMcbEzV4xQBNF=s96-c"
        ),
        "name": "Maximiliano Pezzotta",
        "picture_color": "green-blue",
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
        "picture_color": "green-blue",
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
        "picture_color": "green-blue",
        "blocked": False,
        "roles": None,
        "role": None,
    }

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

    def users_create(self, data: Dict[str, Any]):
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


class FakeOrganization:
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
                            )
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
            200
        )


class FakeAuthClient(AbstractClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.credentials = FakeCredentials()
        self.profile = FakeProfile()
        self.role = FakeRoles()
        self.user = FakeUsers()
        self.organization = FakeOrganization()
