from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceResponse,
)
from app.services.maintenance_service import (
    MaintenanceService,
)

router = APIRouter(
    prefix="/maintenances",
    tags=["Maintenances"],
)

service = MaintenanceService()


@router.post(
    "",
    response_model=MaintenanceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_maintenance(
    payload: MaintenanceCreate,
    db: Session = Depends(get_db),
):
    return service.create(db, payload)