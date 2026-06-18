from __future__ import annotations
import enum
from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EquipmentStatus(str, enum.Enum):
    AVAILABLE = "available"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"


class Equipment(Base):

    __tablename__ = "equipments"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    serial_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    status: Mapped[EquipmentStatus] = mapped_column(
        Enum(EquipmentStatus, name="equipment_status"),
        default=EquipmentStatus.AVAILABLE,
        nullable=False,
    )

    reservations: Mapped[list["Reservation"]] = relationship(
        back_populates="equipment"
    )

    maintenances: Mapped[list["Maintenance"]] = relationship(
        back_populates="equipment"
    )