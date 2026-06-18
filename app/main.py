from fastapi import FastAPI

from app.core.handlers import register_exception_handlers
from app.routers.equipments import router as equipment_router
from app.routers.maintenances import router as maintenance_router
from app.routers.reservations import router as reservation_router
from app.routers.users import router as user_router

app = FastAPI(
    title="Equipment Reservation API",
    version="1.0.0",
)

register_exception_handlers(app)

app.include_router(user_router)
app.include_router(equipment_router)
app.include_router(maintenance_router)
app.include_router(reservation_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}