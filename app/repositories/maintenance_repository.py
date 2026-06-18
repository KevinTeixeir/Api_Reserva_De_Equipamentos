from datetime import datetime

from sqlalchemy.orm import Session

from app.models.maintenance import (
    Maintenance,
    MaintenanceStatus,
)


class MaintenanceRepository:

    def create(
        self,
        db: Session,
        maintenance: Maintenance,
    ) -> Maintenance:

        db.add(maintenance)
        db.flush()
        db.refresh(maintenance)

        return maintenance

    def has_active_maintenance(
        self,
        db: Session,
        equipment_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> bool:

        maintenance = (
            db.query(Maintenance)
            .filter(
                Maintenance.equipment_id == equipment_id,
                Maintenance.status.in_(
                    [
                        MaintenanceStatus.SCHEDULED,
                        MaintenanceStatus.ACTIVE,
                    ]
                ),
                Maintenance.start_date < end_date,
                Maintenance.end_date > start_date,
            )
            .first()
        )

        return maintenance is not None