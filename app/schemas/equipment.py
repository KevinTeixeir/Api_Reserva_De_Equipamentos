from pydantic import Field

from app.models.equipment import EquipmentStatus
from app.schemas.common import BaseSchema


class EquipmentCreate(BaseSchema):
    name: str = Field(min_length=3, max_length=120)
    category: str = Field(min_length=2, max_length=80)
    serial_number: str = Field(min_length=3, max_length=100)


class EquipmentResponse(BaseSchema):
    id: int
    name: str
    category: str
    serial_number: str
    status: EquipmentStatus


class EquipmentStatusUpdate(BaseSchema):
    status: EquipmentStatus


class EquipmentStatistics(BaseSchema):
    equipment_id: int
    reservation_hours: float
    available_hours: float
    utilization_rate: float