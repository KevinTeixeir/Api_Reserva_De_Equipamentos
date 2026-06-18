from datetime import datetime

from pydantic import Field, model_validator

from app.models.reservation import ReservationStatus
from app.schemas.common import BaseSchema


class ReservationCreate(BaseSchema):
    user_id: int
    equipment_id: int
    start_date: datetime
    end_date: datetime
    purpose: str = Field(min_length=5, max_length=255)

    @model_validator(mode="after")
    def validate_dates(self):

        if self.end_date <= self.start_date:
            raise ValueError(
                "end_date must be greater than start_date"
            )

        return self


class ReservationResponse(BaseSchema):
    id: int
    user_id: int
    equipment_id: int
    start_date: datetime
    end_date: datetime
    purpose: str
    status: ReservationStatus
    created_at: datetime
    updated_at: datetime


class ReservationStatusUpdate(BaseSchema):
    status: ReservationStatus


class ReservationFilter(BaseSchema):
    status: ReservationStatus | None = None
    equipment_id: int | None = None
    user_id: int | None = None
    limit: int = 10
    offset: int = 0