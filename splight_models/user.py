from typing import List, Optional

from .base import SplightBaseModel


class User(SplightBaseModel):
    user_id: str
    organization_id: str
    username: str
    name: str
    email: str
    picture: str
    permissions: List[str]
    role: Optional[str] = None
    language: str
    theme: str
    picture_color: str
    is_authenticated: bool = True

    def has_any_permission(self, permissions: List[str]) -> bool:
        return any(set(self.permissions).intersection(permissions))

    def __str__(self) -> str:
        return self.username

    def __repr__(self) -> str:
        return self.username


class OrganizationMetadata(SplightBaseModel):
    billing_id: Optional[str] = None
    blockchain_id: Optional[str] = None


class Organization(SplightBaseModel):
    id: str
    name: str
    display_name: str
    metadata: OrganizationMetadata = OrganizationMetadata()
