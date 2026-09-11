from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.content import Chapter, Grade, KnowledgePoint, Lesson, Subject


class ContentRepository:
    def __init__(self, db: Session):
        self.db = db

    # Subject
    def create_subject(self, name: str, description: str) -> Subject:
        obj = Subject(name=name, description=description)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def list_subjects(self) -> list[Subject]:
        return list(self.db.execute(select(Subject)).scalars().all())

    def get_subject(self, subject_id: str) -> Optional[Subject]:
        return self.db.get(Subject, subject_id)

    # Grade
    def create_grade(self, subject_id: str, name: str) -> Grade:
        obj = Grade(subject_id=subject_id, name=name)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def list_grades(self, subject_id: Optional[str] = None) -> list[Grade]:
        stmt = select(Grade)
        if subject_id:
            stmt = stmt.where(Grade.subject_id == subject_id)
        return list(self.db.execute(stmt).scalars().all())

    def get_grade(self, grade_id: str) -> Optional[Grade]:
        return self.db.get(Grade, grade_id)

    # Chapter
    def create_chapter(self, grade_id: str, name: str, order: int) -> Chapter:
        obj = Chapter(grade_id=grade_id, name=name, order=order)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def list_chapters(self, grade_id: Optional[str] = None) -> list[Chapter]:
        stmt = select(Chapter).order_by(Chapter.order)
        if grade_id:
            stmt = stmt.where(Chapter.grade_id == grade_id)
        return list(self.db.execute(stmt).scalars().all())

    def get_chapter(self, chapter_id: str) -> Optional[Chapter]:
        return self.db.get(Chapter, chapter_id)

    # Lesson
    def create_lesson(self, chapter_id: str, name: str, content: str, order: int) -> Lesson:
        obj = Lesson(chapter_id=chapter_id, name=name, content=content, order=order)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def list_lessons(self, chapter_id: Optional[str] = None) -> list[Lesson]:
        stmt = select(Lesson).order_by(Lesson.order)
        if chapter_id:
            stmt = stmt.where(Lesson.chapter_id == chapter_id)
        return list(self.db.execute(stmt).scalars().all())

    def get_lesson(self, lesson_id: str) -> Optional[Lesson]:
        return self.db.get(Lesson, lesson_id)

    # KnowledgePoint
    def create_knowledge_point(self, lesson_id: str, name: str) -> KnowledgePoint:
        obj = KnowledgePoint(lesson_id=lesson_id, name=name)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def list_knowledge_points(self, lesson_id: Optional[str] = None) -> list[KnowledgePoint]:
        stmt = select(KnowledgePoint)
        if lesson_id:
            stmt = stmt.where(KnowledgePoint.lesson_id == lesson_id)
        return list(self.db.execute(stmt).scalars().all())

    def get_knowledge_point(self, kp_id: str) -> Optional[KnowledgePoint]:
        return self.db.get(KnowledgePoint, kp_id)
