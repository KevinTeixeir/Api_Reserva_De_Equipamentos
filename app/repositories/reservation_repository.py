from datetime import datetime

from sqlalchemy.orm import Session

from app.models.equipment import Equipment
from app.models.reservation import (
    Reservation,
    ReservationStatus,
)


class ReservationRepository:

    def get_by_id(
        self,
        db: Session,
        reservation_id: int,
    ) -> Reservation | None:

        return (
            db.query(Reservation)
            .filter(
                Reservation.id == reservation_id
            )
            .first()
        )

    def create(
        self,
        db: Session,
        reservation: Reservation,
    ) -> Reservation:

        db.add(reservation)
        db.flush()
        db.refresh(reservation)

        return reservation

    def update(
        self,
        db: Session,
        reservation: Reservation,
    ) -> Reservation:

        db.add(reservation)
        db.flush()
        db.refresh(reservation)

        return reservation

    def count_future_reservations(
        self,
        db: Session,
        user_id: int,
    ) -> int:

        return (
            db.query(Reservation)
            .filter(
                Reservation.user_id == user_id,
                Reservation.start_date > datetime.utcnow(),
                Reservation.status.in_(
                    [
                        ReservationStatus.DRAFT,
                        ReservationStatus.CONFIRMED,
                    ]
                ),
            )
            .count()
        )

    def find_conflicting_reservation(
        self,
        db: Session,
        equipment_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> Reservation | None:

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
                Reservation.start_date < end_date,
                Reservation.end_date > start_date,
            )
            .first()
        )
    def list(
        self,
        db: Session,
        status: ReservationStatus | None = None,
        equipment_id: int | None = None,
        user_id: int | None = None,
        limit: int = 10,
        offset: int = 0,
    ):

        query = db.query(Reservation)

        if status:
            query = query.filter(
                Reservation.status == status
            )

        if equipment_id:
            query = query.filter(
                Reservation.equipment_id == equipment_id
            )

        if user_id:
            query = query.filter(
                Reservation.user_id == user_id
            )

        total = query.count()

        items = (
            query
            .order_by(Reservation.start_date.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return total, items

    def lock_equipment(
        self,
        db: Session,
        equipment_id: int,
    ) -> Equipment | None:

        return (
            db.query(Equipment)
            .filter(
                Equipment.id == equipment_id
            )
            .with_for_update()
            .first()
        )