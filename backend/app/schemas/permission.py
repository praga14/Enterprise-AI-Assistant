from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PermissionCreate(BaseModel):
    name: str
    description: str | None = None
    resource: str
    action: str


class PermissionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    resource: str | None = None
    action: str | None = None
    is_active: bool | None = None


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    resource: str
    action: str
    is_active: bool
    is_system: bool
    created_at: datetime
    updated_at: datetime