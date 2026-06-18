from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import and_, or_

from app.models.reservation import Reservation
from app.models.reservation import ReservationStatus
from app.core.database import Base


class ReservationHistory(Base):
    __tablename__ = "reservation_history"

    id: Mapped[int] = mapped_column(primary_key=True)

    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservations.id"),
        nullable=False,
    )

    previous_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    new_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    reservation: Mapped["Reservation"] = relationship(
        back_populates="history"
    )
    
def find_conflict(
    self,
    db,
    equipment_id: int,
    start_date,
    end_date,
):
    return (
        db.query(Reservation)
        .filter(
            Reservation.equipment_id == equipment_id,
            Reservation.status.in_(
                [
                    ReservationStatus.DRAFT,
                    ReservationStatus.CONFIRMED,
                    ReservationStatus.IN_USE,
                ]
            ),
            and_(
                Reservation.start_date < end_date,
                Reservation.end_date > start_date,
            ),
        )
        .first()
    )