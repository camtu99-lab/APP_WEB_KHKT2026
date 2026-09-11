from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.role import RoleName
from app.models.user import User
from app.schemas.content import (
    ChapterCreate,
    ChapterResponse,
    GradeCreate,
    GradeResponse,
    KnowledgePointCreate,
    KnowledgePointResponse,
    LessonCreate,
    LessonResponse,
    SubjectCreate,
    SubjectResponse,
)
from app.services.content_service import ContentService

router = APIRouter(prefix="/api/v1", tags=["content"])

write_roles = require_roles(RoleName.TEACHER, RoleName.ADMIN)


@router.post("/subjects", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(payload: SubjectCreate, db: Session = Depends(get_db), _user: User = Depends(write_roles)):
    return ContentService(db).create_subject(payload)


@router.get("/subjects", response_model=list[SubjectResponse])
def list_subjects(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    return ContentService(db).list_subjects()


@router.post("/grades", response_model=GradeResponse, status_code=status.HTTP_201_CREATED)
def create_grade(payload: GradeCreate, db: Session = Depends(get_db), _user: User = Depends(write_roles)):
    return ContentService(db).create_grade(payload)


@router.get("/grades", response_model=list[GradeResponse])
def list_grades(
    subject_id: Optional[str] = None, db: Session = Depends(get_db), _user: User = Depends(get_current_user)
):
    return ContentService(db).list_grades(subject_id)


@router.post("/chapters", response_model=ChapterResponse, status_code=status.HTTP_201_CREATED)
def create_chapter(payload: ChapterCreate, db: Session = Depends(get_db), _user: User = Depends(write_roles)):
    return ContentService(db).create_chapter(payload)


@router.get("/chapters", response_model=list[ChapterResponse])
def list_chapters(
    grade_id: Optional[str] = None, db: Session = Depends(get_db), _user: User = Depends(get_current_user)
):
    return ContentService(db).list_chapters(grade_id)


@router.post("/lessons", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def create_lesson(payload: LessonCreate, db: Session = Depends(get_db), _user: User = Depends(write_roles)):
    return ContentService(db).create_lesson(payload)


@router.get("/lessons", response_model=list[LessonResponse])
def list_lessons(
    chapter_id: Optional[str] = None, db: Session = Depends(get_db), _user: User = Depends(get_current_user)
):
    return ContentService(db).list_lessons(chapter_id)


@router.post("/knowledge-points", response_model=KnowledgePointResponse, status_code=status.HTTP_201_CREATED)
def create_knowledge_point(
    payload: KnowledgePointCreate, db: Session = Depends(get_db), _user: User = Depends(write_roles)
):
    return ContentService(db).create_knowledge_point(payload)


@router.get("/knowledge-points", response_model=list[KnowledgePointResponse])
def list_knowledge_points(
    lesson_id: Optional[str] = None, db: Session = Depends(get_db), _user: User = Depends(get_current_user)
):
    return ContentService(db).list_knowledge_points(lesson_id)
