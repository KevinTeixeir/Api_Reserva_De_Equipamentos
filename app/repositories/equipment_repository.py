from sqlalchemy.orm import Session

from app.models.equipment import Equipment


class EquipmentRepository:

    def get_by_id(
        self,
        db: Session,
        equipment_id: int,
    ) -> Equipment | None:

        return (
            db.query(Equipment)
            .filter(Equipment.id == equipment_id)
            .first()
        )

    def get_by_serial_number(
        self,
        db: Session,
        serial_number: str,
    ) -> Equipment | None:

        return (
            db.query(Equipment)
            .filter(
                Equipment.serial_number == serial_number
            )
            .first()
        )

    def list(
        self,
        db: Session,
        status: str | None = None,
        category: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ):

        query = db.query(Equipment)

        if status:
            query = query.filter(
                Equipment.status == status
            )

        if category:
            query = query.filter(
                Equipment.category == category
            )

        total = query.count()

        items = (
            query
            .offset(offset)
            .limit(limit)
            .all()
        )

        return total, items

    def create(
        self,
        db: Session,
        equipment: Equipment,
    ) -> Equipment:

        db.add(equipment)
        db.flush()
        db.refresh(equipment)

        return equipment

    def update(
        self,
        db: Session,
        equipment: Equipment,
    ) -> Equipment:

        db.add(equipment)
        db.flush()
        db.refresh(equipment)

        return equipment