from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.role import RoleName
from app.models.user import User
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.name,
        is_active=current_user.is_active,
    )


@router.get("", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_roles(RoleName.ADMIN)),
):
    # Chỉ ADMIN mới xem được danh sách toàn bộ user — minh họa RBAC.
    users = db.execute(select(User)).scalars().all()
    return [
        UserResponse(id=u.id, email=u.email, full_name=u.full_name, role=u.role.name, is_active=u.is_active)
        for u in users
    ]
