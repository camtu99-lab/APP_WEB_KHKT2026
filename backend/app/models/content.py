import uuid

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin


def _uuid_default():
    return str(uuid.uuid4())


class Subject(Base, TimestampMixin):
    __tablename__ = "subjects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_default)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")

    grades: Mapped[list["Grade"]] = relationship(back_populates="subject", cascade="all, delete-orphan")


class Grade(Base, TimestampMixin):
    __tablename__ = "grades"
    __table_args__ = (UniqueConstraint("subject_id", "name", name="uq_grade_subject_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_default)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # vd: "Lớp 10", "Lớp 11", "Lớp 12"

    subject: Mapped["Subject"] = relationship(back_populates="grades")
    chapters: Mapped[list["Chapter"]] = relationship(back_populates="grade", cascade="all, delete-orphan")


class Chapter(Base, TimestampMixin):
    __tablename__ = "chapters"
    __table_args__ = (UniqueConstraint("grade_id", "name", name="uq_chapter_grade_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_default)
    grade_id: Mapped[str] = mapped_column(ForeignKey("grades.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0)

    grade: Mapped["Grade"] = relationship(back_populates="chapters")
    lessons: Mapped[list["Lesson"]] = relationship(back_populates="chapter", cascade="all, delete-orphan")


class Lesson(Base, TimestampMixin):
    __tablename__ = "lessons"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_default)
    chapter_id: Mapped[str] = mapped_column(ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, default="")
    order: Mapped[int] = mapped_column(Integer, default=0)

    chapter: Mapped["Chapter"] = relationship(back_populates="lessons")
    knowledge_points: Mapped[list["KnowledgePoint"]] = relationship(
        back_populates="lesson", cascade="all, delete-orphan"
    )


class KnowledgePoint(Base, TimestampMixin):
    __tablename__ = "knowledge_points"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_default)
    lesson_id: Mapped[str] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    lesson: Mapped["Lesson"] = relationship(back_populates="knowledge_points")
