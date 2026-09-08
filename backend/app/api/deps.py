from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.db.session import get_db
from app.models.role import RoleName
from app.models.user import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    if token is None:
        raise UnauthorizedError(code="MISSING_TOKEN", message="Thiếu access token")

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise UnauthorizedError(code="INVALID_TOKEN", message="Access token không hợp lệ hoặc hết hạn")

    user = UserRepository(db).get_by_id(payload["sub"])
    if user is None or not user.is_active:
        raise UnauthorizedError(code="USER_NOT_FOUND", message="Người dùng không tồn tại hoặc bị khóa")

    return user


def require_roles(*allowed: RoleName):
    """
    Dependency factory dùng cho RBAC ở route, ví dụ:
    Depends(require_roles(RoleName.TEACHER, RoleName.ADMIN))
    """

    def _checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.name not in set(allowed):
            raise ForbiddenError(
                code="ROLE_NOT_ALLOWED",
                message=f"Role '{current_user.role.name.value}' không có quyền thực hiện hành động này",
            )
        return current_user

    return _checker
