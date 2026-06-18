class BusinessException(Exception):
    def __init__(
        self,
        error: str,
        message: str,
        status_code: int = 400,
        details: dict | None = None,
    ):
        self.error = error
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class NotFoundException(BusinessException):
    def __init__(self, resource: str, resource_id: int):
        super().__init__(
            error="RESOURCE_NOT_FOUND",
            message=f"{resource} não encontrado.",
            status_code=404,
            details={"id": resource_id},
        )