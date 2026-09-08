from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, user_id: str, token_hash: str, expires_at: datetime) -> RefreshToken:
        rt = RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self.db.add(rt)
        self.db.commit()
        self.db.refresh(rt)
        return rt

    def get_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        return self.db.execute(stmt).scalar_one_or_none()

    def revoke(self, token: RefreshToken) -> None:
        token.revoked = True
        self.db.add(token)
        self.db.commit()

    def is_valid(self, token: Optional[RefreshToken]) -> bool:
        if token is None or token.revoked:
            return False
        expires_at = token.expires_at
        if expires_at.tzinfo is None:
            # SQLite (dùng khi test) không lưu tzinfo; Postgres (production) thì có.
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return expires_at > datetime.now(timezone.utc)
