import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin


def _uuid_default():
    return str(uuid.uuid4())


class ExamStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    CLOSED = "CLOSED"


class AttemptStatus(str, enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"


class Exam(Base, TimestampMixin):
    __tablename__ = "exams"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_default)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[ExamStatus] = mapped_column(SAEnum(ExamStatus, name="exam_status"), default=ExamStatus.DRAFT)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    exam_questions: Mapped[list["ExamQuestion"]] = relationship(
        back_populates="exam", cascade="all, delete-orphan", order_by="ExamQuestion.order"
    )


class ExamQuestion(Base, TimestampMixin):
    __tablename__ = "exam_questions"
    __table_args__ = (UniqueConstraint("exam_id", "question_id", name="uq_exam_question"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_default)
    exam_id: Mapped[str] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id: Mapped[str] = mapped_column(
        ForeignKey("questions.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    order: Mapped[int] = mapped_column(Integer, default=0)
    points: Mapped[float] = mapped_column(Float, default=1.0)

    exam: Mapped["Exam"] = relationship(back_populates="exam_questions")
    question: Mapped["Question"] = relationship()  # noqa: F821


class Attempt(Base, TimestampMixin):
    __tablename__ = "attempts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_default)
    exam_id: Mapped[str] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[AttemptStatus] = mapped_column(
        SAEnum(AttemptStatus, name="attempt_status"), default=AttemptStatus.IN_PROGRESS
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)

    exam: Mapped["Exam"] = relationship()
    answers: Mapped[list["Answer"]] = relationship(back_populates="attempt", cascade="all, delete-orphan")


class Answer(Base, TimestampMixin):
    __tablename__ = "answers"
    __table_args__ = (UniqueConstraint("attempt_id", "question_id", name="uq_attempt_question"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_default)
    attempt_id: Mapped[str] = mapped_column(ForeignKey("attempts.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id: Mapped[str] = mapped_column(
        ForeignKey("questions.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    selected_option_ids: Mapped[str] = mapped_column(Text, default="")  # JSON list, dùng cho câu trắc nghiệm
    answer_text: Mapped[str] = mapped_column(Text, default="")  # dùng cho SHORT_ANSWER / NUMERICAL
    is_correct: Mapped[bool] = mapped_column(default=False)
    points_earned: Mapped[float] = mapped_column(Float, default=0.0)

    attempt: Mapped["Attempt"] = relationship(back_populates="answers")
