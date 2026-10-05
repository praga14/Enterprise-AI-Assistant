from pydantic import BaseModel


class UserRoleCreate(BaseModel):
    user_id: int
    role_id: int