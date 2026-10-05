from pydantic import BaseModel


class RolePermissionCreate(BaseModel):
    role_id: int
    permission_id: int