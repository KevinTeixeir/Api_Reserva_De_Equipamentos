from __future__ import annotations
import enum
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.core.database import Base


class MaintenanceStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    FINISHED = "finished"


class Maintenance(Base):
    __tablename__ = "maintenances"

    id: Mapped[int] = mapped_column(primary_key=True)

    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipments.id"),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    end_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    status: Mapped[MaintenanceStatus] = mapped_column(
        Enum(
            MaintenanceStatus,
            name="maintenance_status",
        ),
        default=MaintenanceStatus.SCHEDULED,
        nullable=False,
    )

    equipment: Mapped["Equipment"] = relationship(
        back_populates="maintenances"
    )