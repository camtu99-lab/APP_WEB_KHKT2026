from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.role import Role, RoleName
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.get(User, user_id)

    def get_role_by_name(self, name: RoleName) -> Optional[Role]:
        stmt = select(Role).where(Role.name == name)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, *, email: str, full_name: str, hashed_password: str, role_id: int) -> User:
        user = User(email=email, full_name=full_name, hashed_password=hashed_password, role_id=role_id)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
