from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.role import RoleName
from app.models.user import User
from app.schemas.exam import (
    AttemptResultResponse,
    AttemptStartResponse,
    AttemptSubmitRequest,
    ExamCreate,
    ExamListItem,
    ExamQuestionAdd,
    ExamResponse,
)
from app.services.exam_service import ExamService

router = APIRouter(prefix="/api/v1/exams", tags=["exams"])
attempts_router = APIRouter(prefix="/api/v1/attempts", tags=["attempts"])

write_roles = require_roles(RoleName.TEACHER, RoleName.ADMIN)


@router.post("", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
def create_exam(payload: ExamCreate, db: Session = Depends(get_db), user: User = Depends(write_roles)):
    exam = ExamService(db).create_exam(payload, created_by=user.id)
    return ExamService(db).get_exam(exam.id)


@router.post("/{exam_id}/questions", response_model=ExamResponse)
def add_question_to_exam(
    exam_id: str, payload: ExamQuestionAdd, db: Session = Depends(get_db), _user: User = Depends(write_roles)
):
    return ExamService(db).add_question(exam_id, payload)


@router.post("/{exam_id}/publish", response_model=ExamResponse)
def publish_exam(exam_id: str, db: Session = Depends(get_db), _user: User = Depends(write_roles)):
    ExamService(db).publish_exam(exam_id)
    return ExamService(db).get_exam(exam_id)


@router.get("", response_model=list[ExamListItem])
def list_exams(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    is_student = user.role.name == RoleName.STUDENT
    return ExamService(db).list_exams(is_student=is_student)


@router.get("/{exam_id}", response_model=ExamResponse)
def get_exam(exam_id: str, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    return ExamService(db).get_exam(exam_id)


@router.post("/{exam_id}/start", response_model=AttemptStartResponse, status_code=status.HTTP_201_CREATED)
def start_attempt(exam_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ExamService(db).start_attempt(exam_id, student_id=user.id)


@attempts_router.post("/{attempt_id}/submit", response_model=AttemptResultResponse)
def submit_attempt(
    attempt_id: str, payload: AttemptSubmitRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    # Chấm điểm hoàn toàn ở server (ExamService._grade_single) — client chỉ gửi lựa chọn, không gửi đúng/sai.
    return ExamService(db).submit_attempt(attempt_id, student_id=user.id, answers=payload.answers)


@attempts_router.get("/{attempt_id}/result", response_model=AttemptResultResponse)
def get_attempt_result(attempt_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    is_privileged = user.role.name in (RoleName.TEACHER, RoleName.ADMIN)
    return ExamService(db).get_result(attempt_id, requester_id=user.id, requester_is_privileged=is_privileged)
