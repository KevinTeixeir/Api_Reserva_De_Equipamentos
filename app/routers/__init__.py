from app.routers.equipments import router as equipment_router
from app.routers.maintenances import router as maintenance_router
from app.routers.reservations import router as reservation_router
from app.routers.users import router as user_router

__all__ = [
    "user_router",
    "equipment_router",
    "maintenance_router",
    "reservation_router",
]