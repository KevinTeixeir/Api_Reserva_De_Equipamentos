from datetime import datetime

from pydantic import Field, model_validator

from app.models.maintenance import MaintenanceStatus
from app.schemas.common import BaseSchema


class MaintenanceCreate(BaseSchema):
    equipment_id: int
    description: str = Field(min_length=5, max_length=255)
    start_date: datetime
    end_date: datetime

    @model_validator(mode="after")
    def validate_dates(self):

        if self.end_date <= self.start_date:
            raise ValueError(
                "end_date must be greater than start_date"
            )

        return self


class MaintenanceResponse(BaseSchema):
    id: int
    equipment_id: int
    description: str
    start_date: datetime
    end_date: datetime
    status: MaintenanceStatus