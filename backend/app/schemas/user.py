from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    employee_id: str
    username: str
    full_name: str
    email: EmailStr
    password: str
    department: str | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: str
    username: str
    full_name: str
    email: EmailStr
    department: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    department: str | None = None


class PasswordUpdate(BaseModel):
    new_password: str


class SelfPasswordUpdate(BaseModel):
    current_password: str
    new_password: str