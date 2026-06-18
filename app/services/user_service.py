from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException
from app.core.exceptions import NotFoundException
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate

class UserService:

    def __init__(self):
        self.repository = UserRepository()

    def create(
        self,
        db: Session,
        data: UserCreate,
    ) -> User:

        existing = self.repository.get_by_email(
            db,
            data.email,
        )

        if existing:
            raise BusinessException(
                error="EMAIL_ALREADY_EXISTS",
                message="Já existe um usuário com este e-mail.",
                status_code=409,
            )

        user = User(
            name=data.name,
            email=data.email,
        )

        self.repository.create(db, user)

        db.commit()

        return user

    def update_status(
        self,
        db: Session,
        user_id: int,
        status,
    ) -> User:

        user = self.repository.get_by_id(
            db,
            user_id,
        )

        if not user:
            raise NotFoundException(
                "Usuário",
                user_id,
            )

        user.status = status

        self.repository.update(db, user)

        db.commit()

        return user