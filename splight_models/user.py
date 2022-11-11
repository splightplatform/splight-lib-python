from datetime import datetime
from typing import Dict, List, Optional

from splight_models.base import SplightBaseModel


class Role(SplightBaseModel):
    id: str
    name: str
    description: Optional[str] = None
    permission: List = []


class UserMetadata(SplightBaseModel):
    language: str = "en"
    theme: str = "dark"
    picture_color: str = "light-green"


class AppMetadata(SplightBaseModel):
    is_manager: bool = False


class User(SplightBaseModel):
    user_id: str
    organization_id: Optional[str] = None
    username: Optional[str] = None
    name: str
    email: str
    picture: str
    permissions: Optional[List[str]] = None
    last_login: Optional[datetime] = None
    # picture_color: Optional[str] = None
    roles: Optional[List[Dict]] = None
    role: Optional[str] = None
    user_metadata: Optional[UserMetadata] = None
    app_metadata: Optional[AppMetadata] = None
    is_authenticated: bool = True
    blocked: Optional[bool] = None

    @property
    def is_anonymous(self):
        return False

    def has_any_permission(self, permissions: List[str]) -> bool:
        return any(set(self.permissions).intersection(permissions))

    def __str__(self) -> str:
        return self.email

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class OrganizationMetadata(SplightBaseModel):
    billing_id: Optional[str] = None
    blockchain_id: Optional[str] = None
    manager_email: Optional[str] = None


class Organization(SplightBaseModel):
    id: str
    name: str
    display_name: str
    metadata: OrganizationMetadata = OrganizationMetadata()


class Inviter(SplightBaseModel):
    name: str


class Invitee(SplightBaseModel):
    email: str


class Invitation(SplightBaseModel):
    id: Optional[str] = None
    organization_id: Optional[str] = None
    inviter: Inviter
    invitee: Invitee
    app_metadata: AppMetadata
    user_metadata: UserMetadata
    invitation_url: str
    created_at: datetime
    expires_at: datetime
    client_id: str
    roles: List[str] = []
    ticket_id: str
