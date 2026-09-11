from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.question import Difficulty, QuestionStatus, QuestionType
from app.models.role import RoleName
from app.models.user import User
from app.schemas.question import QuestionCreate, QuestionResponse, QuestionSearchParams, QuestionUpdateStatus
from app.services.question_service import QuestionService

router = APIRouter(prefix="/api/v1/questions", tags=["questions"])

write_roles = require_roles(RoleName.TEACHER, RoleName.ADMIN)


@router.post("", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
def create_question(payload: QuestionCreate, db: Session = Depends(get_db), user: User = Depends(write_roles)):
    return QuestionService(db).create_question(payload, created_by=user.id)


@router.get("", response_model=list[QuestionResponse])
def search_questions(
    knowledge_point_id: Optional[str] = None,
    type: Optional[QuestionType] = None,
    difficulty: Optional[Difficulty] = None,
    status_filter: Optional[QuestionStatus] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    params = QuestionSearchParams(
        knowledge_point_id=knowledge_point_id,
        type=type,
        difficulty=difficulty,
        status=status_filter,
        keyword=keyword,
    )
    return QuestionService(db).search(params, requester_role=user.role.name)


@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(question_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return QuestionService(db).get_question(question_id, requester_role=user.role.name)


@router.patch("/{question_id}/status", response_model=QuestionResponse)
def update_question_status(
    question_id: str,
    payload: QuestionUpdateStatus,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Teacher/Admin duyệt câu hỏi (kể cả câu AI sinh ra) — RBAC kiểm tra trong service.
    return QuestionService(db).update_status(question_id, payload.status, requester_role=user.role.name)
