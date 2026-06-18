from typing import Any

from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: dict[str, Any] = {}


class PaginationParams(BaseModel):
    limit: int = 10
    offset: int = 0


class PaginatedResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[Any]


class MessageResponse(BaseModel):
    message: str


class StatusUpdateResponse(BaseModel):
    message: str
    previous_status: str
    current_status: str


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)