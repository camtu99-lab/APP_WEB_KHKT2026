import hashlib
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.role import RoleName
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


def _hash_token(token: str) -> str:
    # Không lưu refresh token dạng plaintext trong DB.
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.refresh_tokens = RefreshTokenRepository(db)

    def register(self, data: RegisterRequest) -> User:
        if self.users.get_by_email(data.email):
            raise ConflictError(code="EMAIL_ALREADY_EXISTS", message="Email đã được sử dụng")

        role = self.users.get_role_by_name(data.role)
        if role is None:
            raise UnauthorizedError(code="ROLE_NOT_FOUND", message="Role chưa được khởi tạo (chạy seed trước)")

        user = self.users.create(
            email=data.email,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
            role_id=role.id,
        )
        return user

    def _issue_tokens(self, user: User) -> TokenResponse:
        access_token = create_access_token(subject=user.id, role=user.role.name.value)
        refresh_token = create_refresh_token(subject=user.id)

        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        self.refresh_tokens.create(
            user_id=user.id, token_hash=_hash_token(refresh_token), expires_at=expires_at
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    def login(self, data: LoginRequest) -> TokenResponse:
        user = self.users.get_by_email(data.email)
        if user is None or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedError(code="INVALID_CREDENTIALS", message="Email hoặc mật khẩu không đúng")
        if not user.is_active:
            raise UnauthorizedError(code="ACCOUNT_DISABLED", message="Tài khoản đã bị khóa")
        return self._issue_tokens(user)

    def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise UnauthorizedError(code="INVALID_REFRESH_TOKEN", message="Refresh token không hợp lệ")

        stored = self.refresh_tokens.get_by_hash(_hash_token(refresh_token))
        if not self.refresh_tokens.is_valid(stored):
            raise UnauthorizedError(code="REFRESH_TOKEN_REVOKED", message="Refresh token đã hết hạn hoặc bị thu hồi")

        user = self.users.get_by_id(payload["sub"])
        if user is None or not user.is_active:
            raise UnauthorizedError(code="USER_NOT_FOUND", message="Người dùng không tồn tại")

        # Rotate: thu hồi refresh token cũ, phát hành cặp token mới.
        self.refresh_tokens.revoke(stored)
        return self._issue_tokens(user)

    def logout(self, refresh_token: str) -> None:
        stored = self.refresh_tokens.get_by_hash(_hash_token(refresh_token))
        if stored is not None:
            self.refresh_tokens.revoke(stored)
