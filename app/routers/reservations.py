from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.reservation import (
    ReservationCreate,
    ReservationResponse,
    ReservationStatusUpdate,
)
from app.services.reservation_service import (
    ReservationService,
)

router = APIRouter(
    prefix="/reservations",
    tags=["Reservations"],
)

service = ReservationService()


@router.post(
    "",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_reservation(
    payload: ReservationCreate,
    db: Session = Depends(get_db),
):
    return service.create(db, payload)


@router.get(
    "",
    response_model=PaginatedResponse,
)
def list_reservations(
    status: str | None = None,
    equipment_id: int | None = None,
    user_id: int | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    total, items = service.list(
        db=db,
        status=status,
        equipment_id=equipment_id,
        user_id=user_id,
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
    "/{reservation_id}/status",
    response_model=ReservationResponse,
)
def update_reservation_status(
    reservation_id: int,
    payload: ReservationStatusUpdate,
    db: Session = Depends(get_db),
):
    return service.update_status(
        db,
        reservation_id,
        payload.status,
    )