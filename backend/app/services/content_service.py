from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.content import Chapter, Grade, KnowledgePoint, Lesson, Subject
from app.repositories.content_repository import ContentRepository
from app.schemas.content import ChapterCreate, GradeCreate, KnowledgePointCreate, LessonCreate, SubjectCreate


class ContentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ContentRepository(db)

    def create_subject(self, data: SubjectCreate) -> Subject:
        return self.repo.create_subject(name=data.name, description=data.description)

    def list_subjects(self) -> list[Subject]:
        return self.repo.list_subjects()

    def create_grade(self, data: GradeCreate) -> Grade:
        if self.repo.get_subject(data.subject_id) is None:
            raise NotFoundError(code="SUBJECT_NOT_FOUND", message="Môn học không tồn tại")
        return self.repo.create_grade(subject_id=data.subject_id, name=data.name)

    def list_grades(self, subject_id: str | None) -> list[Grade]:
        return self.repo.list_grades(subject_id)

    def create_chapter(self, data: ChapterCreate) -> Chapter:
        if self.repo.get_grade(data.grade_id) is None:
            raise NotFoundError(code="GRADE_NOT_FOUND", message="Lớp/khối không tồn tại")
        return self.repo.create_chapter(grade_id=data.grade_id, name=data.name, order=data.order)

    def list_chapters(self, grade_id: str | None) -> list[Chapter]:
        return self.repo.list_chapters(grade_id)

    def create_lesson(self, data: LessonCreate) -> Lesson:
        if self.repo.get_chapter(data.chapter_id) is None:
            raise NotFoundError(code="CHAPTER_NOT_FOUND", message="Chương không tồn tại")
        return self.repo.create_lesson(
            chapter_id=data.chapter_id, name=data.name, content=data.content, order=data.order
        )

    def list_lessons(self, chapter_id: str | None) -> list[Lesson]:
        return self.repo.list_lessons(chapter_id)

    def create_knowledge_point(self, data: KnowledgePointCreate) -> KnowledgePoint:
        if self.repo.get_lesson(data.lesson_id) is None:
            raise NotFoundError(code="LESSON_NOT_FOUND", message="Bài học không tồn tại")
        return self.repo.create_knowledge_point(lesson_id=data.lesson_id, name=data.name)

    def list_knowledge_points(self, lesson_id: str | None) -> list[KnowledgePoint]:
        return self.repo.list_knowledge_points(lesson_id)
