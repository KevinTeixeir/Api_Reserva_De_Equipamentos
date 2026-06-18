from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException
from app.core.exceptions import NotFoundException
from app.models.reservation import Reservation
from app.models.reservation import ReservationStatus
from app.models.reservation_history import (
    ReservationHistory,
)
from app.models.user import UserStatus
from app.models.equipment import EquipmentStatus

from app.repositories.user_repository import UserRepository
from app.repositories.equipment_repository import (
    EquipmentRepository,
)
from app.repositories.maintenance_repository import (
    MaintenanceRepository,
)
from app.repositories.reservation_repository import (
    ReservationRepository,
)

from app.schemas.reservation import ReservationCreate

ALLOWED_TRANSITIONS = {
    ReservationStatus.DRAFT: [
        ReservationStatus.CONFIRMED,
        ReservationStatus.CANCELED,
    ],
    ReservationStatus.CONFIRMED: [
        ReservationStatus.IN_USE,
        ReservationStatus.CANCELED,
    ],
    ReservationStatus.IN_USE: [
        ReservationStatus.COMPLETED,
    ],
}

class ReservationService:

    def __init__(self):
        self.repository = ReservationRepository()
        self.user_repository = UserRepository()
        self.equipment_repository = EquipmentRepository()
        self.maintenance_repository = (
            MaintenanceRepository()
        )

    def create(
        self,
        db: Session,
        data: ReservationCreate,
    ) -> Reservation:

        user = self.user_repository.get_by_id(
            db,
            data.user_id,
        )

        if not user:
            raise NotFoundException(
                "Usuário",
                data.user_id,
            )

        if user.status == UserStatus.SUSPENDED:
            raise BusinessException(
                error="USER_SUSPENDED",
                message="Usuário suspenso não pode criar reservas.",
                status_code=403,
            )

        equipment = self.repository.lock_equipment(
            db,
            data.equipment_id,
        )

        if not equipment:
            raise NotFoundException(
                "Equipamento",
                data.equipment_id,
            )

        if equipment.status != EquipmentStatus.AVAILABLE:
            raise BusinessException(
                error="EQUIPMENT_UNAVAILABLE",
                message="Equipamento indisponível.",
                status_code=409,
            )

        active_maintenance = (
            self.maintenance_repository.has_active_maintenance(
                db,
                data.equipment_id,
                data.start_date,
                data.end_date,
            )
        )

        if active_maintenance:
            raise BusinessException(
                error="MAINTENANCE_CONFLICT",
                message="Equipamento em manutenção.",
                status_code=409,
            )

        total = self.repository.count_future_reservations(
            db,
            data.user_id,
        )

        if total >= 3:
            raise BusinessException(
                error="RESERVATION_LIMIT_EXCEEDED",
                message="Usuário atingiu o limite de reservas futuras.",
                status_code=409,
            )

        conflict = self.repository.find_conflicting_reservation(
            db,
            data.equipment_id,
            data.start_date,
            data.end_date,
        )

        if conflict:
            raise BusinessException(
                error="RESERVATION_CONFLICT",
                message="Já existe uma reserva para este período.",
                status_code=409,
                details={
                    "conflicting_reservation_id": conflict.id,
                },
            )

        reservation = Reservation(**data.model_dump())

        self.repository.create(db, reservation)

        db.commit()

        return reservation

    def list(
        self,
        db: Session,
        status=None,
        equipment_id=None,
        user_id=None,
        limit: int = 10,
        offset: int = 0,
    ):

        return self.repository.list(
            db,
            status,
            equipment_id,
            user_id,
            limit,
            offset,
        )

    def update_status(
        self,
        db: Session,
        reservation_id: int,
        new_status: ReservationStatus,
    ) -> Reservation:

        reservation = self.repository.get_by_id(
            db,
            reservation_id,
        )

        if not reservation:
            raise NotFoundException(
                "Reserva",
                reservation_id,
            )

        current_status = reservation.status

        if current_status in [
            ReservationStatus.COMPLETED,
            ReservationStatus.CANCELED,
        ]:
            raise BusinessException(
                error="TERMINAL_STATE",
                message="Não é possível alterar uma reserva finalizada.",
                status_code=409,
            )

        allowed = ALLOWED_TRANSITIONS.get(
            current_status,
            [],
        )

        if new_status not in allowed:
            raise BusinessException(
                error="INVALID_STATUS_TRANSITION",
                message="Transição de estado inválida.",
                status_code=422,
                details={
                    "current_status": current_status,
                    "requested_status": new_status,
                },
            )

        history = ReservationHistory(
            reservation_id=reservation.id,
            previous_status=current_status,
            new_status=new_status,
        )

        db.add(history)

        reservation.status = new_status

        self.repository.update(db, reservation)

        db.commit()

        db.refresh(reservation)

        return reservation