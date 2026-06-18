from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.models.maintenance import Maintenance
from app.repositories.equipment_repository import (
    EquipmentRepository,
)
from app.repositories.maintenance_repository import (
    MaintenanceRepository,
)
from app.schemas.maintenance import MaintenanceCreate

class MaintenanceService:

    def __init__(self):
        self.repository = MaintenanceRepository()
        self.equipment_repository = EquipmentRepository()

    def create(
        self,
        db: Session,
        data: MaintenanceCreate,
    ) -> Maintenance:

        equipment = self.equipment_repository.get_by_id(
            db,
            data.equipment_id,
        )

        if not equipment:
            raise NotFoundException(
                "Equipamento",
                data.equipment_id,
            )

        maintenance = Maintenance(**data.model_dump())

        self.repository.create(db, maintenance)

        db.commit()

        return maintenance