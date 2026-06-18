from pydantic import EmailStr, Field

from app.models.user import UserStatus
from app.schemas.common import BaseSchema


class UserCreate(BaseSchema):
    name: str = Field(min_length=3, max_length=120)
    email: EmailStr


class UserResponse(BaseSchema):
    id: int
    name: str
    email: EmailStr
    status: UserStatus


class UserStatusUpdate(BaseSchema):
    status: UserStatus