from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException
from app.core.exceptions import NotFoundException
from app.models.equipment import Equipment
from app.repositories.equipment_repository import (
    EquipmentRepository,
)
from app.schemas.equipment import EquipmentCreate

class EquipmentService:

    def __init__(self):
        self.repository = EquipmentRepository()

    def create(
        self,
        db: Session,
        data: EquipmentCreate,
    ) -> Equipment:

        existing = self.repository.get_by_serial_number(
            db,
            data.serial_number,
        )

        if existing:
            raise BusinessException(
                error="SERIAL_NUMBER_EXISTS",
                message="Número de série já cadastrado.",
                status_code=409,
            )

        equipment = Equipment(**data.model_dump())

        self.repository.create(db, equipment)

        db.commit()

        return equipment

    def list(
        self,
        db: Session,
        status=None,
        category=None,
        limit: int = 10,
        offset: int = 0,
    ):

        return self.repository.list(
            db,
            status,
            category,
            limit,
            offset,
        )

    def update_status(
        self,
        db: Session,
        equipment_id: int,
        status,
    ):

        equipment = self.repository.get_by_id(
            db,
            equipment_id,
        )

        if not equipment:
            raise NotFoundException(
                "Equipamento",
                equipment_id,
            )

        equipment.status = status

        self.repository.update(db, equipment)

        db.commit()

        return equipment