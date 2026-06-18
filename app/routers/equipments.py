from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.equipment import (
    EquipmentCreate,
    EquipmentResponse,
    EquipmentStatusUpdate,
)
from app.services.equipment_service import EquipmentService

router = APIRouter(
    prefix="/equipments",
    tags=["Equipments"],
)

service = EquipmentService()


@router.post(
    "",
    response_model=EquipmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_equipment(
    payload: EquipmentCreate,
    db: Session = Depends(get_db),
):
    return service.create(db, payload)


@router.get(
    "",
    response_model=PaginatedResponse,
)
def list_equipments(
    status: str | None = None,
    category: str | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    total, items = service.list(
        db=db,
        status=status,
        category=category,
        limit=limit,
        offset=offset,
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }


@router.patch(
    "/{equipment_id}/status",
    response_model=EquipmentResponse,
)
def update_equipment_status(
    equipment_id: int,
    payload: EquipmentStatusUpdate,
    db: Session = Depends(get_db),
):
    return service.update_status(
        db,
        equipment_id,
        payload.status,
    )